import sqlite3
import os
import sys
import argparse
import glob
import time
import requests
import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime


# -------------------
# CLI arguments
# -------------------
parser = argparse.ArgumentParser()
parser.add_argument('--model', help='Path to YOLO model file (example: "runs/detect/train/weights/best.pt")',
                    required=True)
parser.add_argument('--source', help='Image source, can be image file ("test.jpg"), \
                    image folder ("test_dir"), video file ("testvid.mp4"), or index of USB camera ("usb0")', 
                    required=True)
parser.add_argument('--thresh', help='Minimum confidence threshold for displaying detected objects (example: "0.4")',
                    default=0.5)
parser.add_argument('--resolution', help='Resolution in WxH to display inference results at (example: "640x480"), \
                    otherwise, match source resolution',
                    default=None)
parser.add_argument('--record', help='Record results from video or webcam and save it as "demo1.avi". Must specify --resolution argument to record.',
                    action='store_true')

args = parser.parse_args()

# -------------------
# Config (tune here)
# -------------------
FRAME_SKIP = 5      # 0 => process every frame (as you asked). Set >0 to skip frames (reduce CPU)
MIN_CONF_THRESH = float(args.thresh)
USER_RES = args.resolution
RECORD = args.record
POST_TO_SERVER = True  # set False if you don’t want to send
# SERVER_POST_URL = "http://127.0.0.1:5000"  # replace with your CAMS API endpoint
SERVER_POST_URL = "http://127.0.0.1:5000/update_status"  # replace with your CAMS API endpoint
POST_INTERVAL = 10.0  # seconds between updates
last_post_time = time.time()

# -------------------
# Validate model path
# -------------------
model_path = args.model
img_source = args.source

if not os.path.exists(model_path):
    print('ERROR: Model path is invalid or model was not found. Make sure the model filename was entered correctly.')
    sys.exit(1)

# -------------------
# Load model
# -------------------
try:
    model = YOLO(model_path, task='detect')
except Exception as e:
    print("ERROR: Failed to load YOLO model:", e)
    sys.exit(1)

labels = model.names if hasattr(model, 'names') else {}

# -------------------
# Helper lists and extensions
# -------------------
img_ext_list = ['.jpg','.JPG','.jpeg','.JPEG','.png','.PNG','.bmp','.BMP']
vid_ext_list = ['.avi','.mov','.mp4','.mkv','.wmv']

# -------------------
# Determine source type
# -------------------
if os.path.isdir(img_source):
    source_type = 'folder'
elif os.path.isfile(img_source):
    _, ext = os.path.splitext(img_source)
    if ext in img_ext_list:
        source_type = 'image'
    elif ext in vid_ext_list:
        source_type = 'video'
    else:
        print(f'File extension {ext} is not supported.')
        sys.exit(1)
elif img_source.startswith('usb'):
    source_type = 'usb'
    try:
        usb_idx = int(img_source[3:])
    except Exception:
        print('ERROR: usb index parse failed. Example usage: usb0')
        sys.exit(1)
elif img_source.startswith('picamera'):
    source_type = 'picamera'
    try:
        picam_idx = int(img_source[8:])
    except Exception:
        picam_idx = 0
else:
    # allow IP camera / stream URLs and numeric webcam indices passed directly as "0"
    # try parse an integer (webcam index) else assume URL
    try:
        idx = int(img_source)
        source_type = 'usb'
        usb_idx = idx
    except Exception:
        # assume it's a stream url
        # we will check it later by trying to open it
        source_type = 'stream'

# -------------------
# Parse resolution
# -------------------
resize = False
resW = resH = None
if USER_RES:
    try:
        resW, resH = int(USER_RES.split('x')[0]), int(USER_RES.split('x')[1])
        resize = True
    except Exception:
        print("WARNING: --resolution malformed. Expected format '640x480'. Ignoring resolution argument.")
        resize = False
        resW = resH = None

# -------------------
# Recorder setup (only for video / camera / stream)
# -------------------
recorder = None
if RECORD:
    if source_type not in ['video', 'usb', 'stream']:
        print('Recording only works for video, camera, or stream sources. Please try again.')
        sys.exit(1)
    if not resize:
        print('Please specify resolution to record video at using --resolution.')
        sys.exit(1)
    record_name = 'demo1.avi'
    record_fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    recorder = cv2.VideoWriter(record_name, fourcc, record_fps, (resW, resH))

# -------------------
# Load/initialize image source
# -------------------

def update_databases(area_name, people_count):
    if people_count == 0:
        status = "empty"
    elif people_count < 10:
        status = "open"
    elif people_count < 30:
        status = "busy"
    else:
        status = "closed"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert into area-specific DB
    db_name = "library.db"
    conn_area = sqlite3.connect(db_name)
    c_area = conn_area.cursor()
    c_area.execute("""
        INSERT INTO records (timestamp, people_count, status)
        VALUES (?, ?, ?)
    """, (timestamp, people_count, status))
    conn_area.commit()
    conn_area.close()

    print(f"✅ Updated {area_name} ...")


imgs_list = []
cap = None
if source_type == 'image':
    imgs_list = [img_source]
elif source_type == 'folder':
    filelist = sorted(glob.glob(os.path.join(img_source, '*')))
    for file in filelist:
        _, file_ext = os.path.splitext(file)
        if file_ext in img_ext_list:
            imgs_list.append(file)
elif source_type == 'video':
    cap_arg = img_source
    cap = cv2.VideoCapture(cap_arg)
elif source_type == 'usb':
    cap_arg = usb_idx
    cap = cv2.VideoCapture(cap_arg)
elif source_type == 'picamera':
    try:
        from picamera2 import Picamera2
        cap = Picamera2()
        if resize:
            cap.configure(cap.create_video_configuration(main={"format": 'XRGB8888', "size": (resW, resH)}))
        cap.start()
    except Exception as e:
        print("ERROR: Failed to initialize Picamera2:", e)
        sys.exit(1)
elif source_type == 'stream':
    cap = cv2.VideoCapture(img_source)
else:
    print("Unknown source type. Exiting.")
    sys.exit(1)

# If using cv2 capture, check valid
if cap is not None and not cap.isOpened():
    print("ERROR: Could not open video capture. Check source/URL.")
    sys.exit(1)

# -------------------
# Colors for boxes
# -------------------
bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106),
              (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]

# -------------------
# Loop variables for FPS and image counting
# -------------------
avg_frame_rate = 0.0
frame_rate_buffer = []
fps_avg_len = 200
img_count = 0
frame_idx = 0
last_object_count = 0

# -------------------
# Inference loop
# -------------------
try:
    while True:
        t_start = time.perf_counter()

        # Frame acquisition
        frame = None
        if source_type in ('image', 'folder'):
            if img_count >= len(imgs_list):
                print('All images have been processed. Exiting program.')
                break
            img_filename = imgs_list[img_count]
            frame = cv2.imread(img_filename)
            img_count += 1

            if frame is None:
                print(f'WARNING: Could not read image {img_filename}. Skipping.')
                continue

        else:
            # video/usb/stream/picamera
            if source_type == 'picamera':
                frame_bgra = cap.capture_array()
                if frame_bgra is None:
                    print('Unable to capture from Picamera. Exiting.')
                    break
                frame = cv2.cvtColor(np.copy(frame_bgra), cv2.COLOR_BGRA2BGR)
            else:
                ret, frame = cap.read()
                if not ret or frame is None:
                    # If video file ended, break. If camera failed, print and exit.
                    if source_type == 'video':
                        print('Reached end of the video file. Exiting program.')
                        break
                    else:
                        print('Unable to read frames from the camera/stream. Exiting program.')
                        break

        # Optional resize
        if resize:
            try:
                frame = cv2.resize(frame, (resW, resH))
            except Exception as e:
                print("WARNING: Resize failed:", e)

        # FRAME_SKIP logic: if >0, skip model inference on some frames
        if FRAME_SKIP > 0 and (frame_idx % (FRAME_SKIP + 1) != 0):
            # Just display and optionally record without running inference
            if resize:
                display_frame = frame.copy()
            else:
                display_frame = frame
            cv2.imshow('YOLO detection results', display_frame)
            if recorder is not None:
                recorder.write(display_frame)
            frame_idx += 1
            if cv2.waitKey(1) & 0xFF == 27:
                break
            # update FPS bookkeeping quickly (approx)
            t_stop = time.perf_counter()
            frame_rate_calc = float(1.0 / max((t_stop - t_start), 1e-6))
            frame_rate_buffer.append(frame_rate_calc)
            if len(frame_rate_buffer) > fps_avg_len:
                frame_rate_buffer.pop(0)
            avg_frame_rate = float(np.mean(frame_rate_buffer))
            continue

        # -----------------------
        # Run inference (wrapped with try/except so a single bad frame won't crash)
        # -----------------------
        results = None
        try:
            # Using direct call on frame (Ultralytics supports this)
            results = model(frame, verbose=False)
        except Exception as e:
            print("WARNING: model inference failed on this frame:", e)
            # show frame anyway and continue
            cv2.imshow('YOLO detection results', frame)
            if recorder is not None:
                recorder.write(frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            frame_idx += 1
            continue

        # Extract detections safely
        detections = []
        try:
            if results and len(results) > 0:
                detections = results[0].boxes  # Ultralytics Boxes object (iterable)
        except Exception:
            detections = []

        # --- Database setup (Keshab edit 0) ---
        conn = sqlite3.connect("cams.db", check_same_thread=False)
        cursor = conn.cursor()

        # helper function to insert status
        def update_status(area, count):
            # decide status label
            if count == 0:
                status = "empty"
            elif count < 10:
                status = "open"
            elif count < 30:
                status = "busy"
            else:
                status = "full"

            cursor.execute("""
                INSERT INTO area_status (area, people_count, status, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(area) DO UPDATE SET
                    people_count = excluded.people_count,
                    status = excluded.status,
                    updated_at = excluded.updated_at
            """, (area, count, status, int(time.time())))
            conn.commit()   

        object_count = 0
        # Iterate detections
        for i in range(len(detections)):
            try:
                # xyxy as tensor -> ensure CPU -> numpy
                xyxy_tensor = detections[i].xyxy
                try:
                    xyxy_cpu = xyxy_tensor.cpu().numpy().squeeze()
                except Exception:
                    # sometimes it's already numpy
                    xyxy_cpu = np.array(xyxy_tensor).squeeze()
                # if it's a single-detection it may be 1D; ensure shape (4,)
                if xyxy_cpu.ndim == 2:
                    # If multiple boxes (shouldn't happen per index), take first
                    xyxy = xyxy_cpu[0]
                else:
                    xyxy = xyxy_cpu
                xmin, ymin, xmax, ymax = xyxy.astype(int)

                # class and confidence
                # detections[i].cls may be tensor; .item() to scalar
                classidx = int(detections[i].cls.item()) if hasattr(detections[i].cls, 'item') else int(detections[i].cls)
                classname = labels[classidx] if classidx in labels else str(classidx)
                conf = float(detections[i].conf.item()) if hasattr(detections[i].conf, 'item') else float(detections[i].conf)

                # Draw only if above threshold
                if conf >= MIN_CONF_THRESH:
                    color = bbox_colors[classidx % len(bbox_colors)]
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    label = f'{classname}: {int(conf*100)}%'
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    label_ymin = max(ymin, labelSize[1] + 10)
                    cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10), (xmin + labelSize[0], label_ymin + baseLine - 10), color, cv2.FILLED)
                    cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                    object_count += 1
            except Exception as e:
                # protect against any per-detection error
                # print("Per-detection warning:", e)
                continue

        # Draw FPS and count for camera/video sources
        if source_type in ('video', 'usb', 'picamera', 'stream'):
            cv2.putText(frame, f'FPS: {avg_frame_rate:0.2f}', (10,20), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2)

        cv2.putText(frame, f'Number of objects: {object_count}', (10,40), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2)
        cv2.imshow('YOLO detection results', frame)
        last_object_count = object_count
        update_databases("Library", object_count)

        # --- Database update every 10 seconds (Keshab edit 0) --- 
        if 'last_db_time' not in globals():
            last_db_time = 0

        now = time.time()
        if now - last_db_time >= 10:  # every 10 sec
            last_db_time = now
            update_status("Library", object_count)   # change "library" per camera/area
            print(f"📥 Saved to DB: area=Library, count={object_count}")
        # (Keshab edit 1)

        # --- Send data to backend every POST_INTERVAL seconds ---
        if POST_TO_SERVER:
            now = time.time()
            if now - last_post_time >= POST_INTERVAL:
                last_post_time = now
                data = {
                    "area": "Library",             # change this to the actual area name
                    "people_count": object_count,  # send the current detection count
                    "timestamp": int(now)
                }
                try:
                    resp = requests.post(SERVER_POST_URL, json=data, timeout=2)
                    if resp.status_code == 200:
                        # print(f"✅ Sent to server: {data}")
                        print(f"🌐 Sent to server ...")
                    else:
                        print("⚠️ Server error:", resp.status_code)
                except Exception as e:
                    print("⚠️ Failed to POST to server:", e)


        # Keys: q to quit, s to pause, p to save frame
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.waitKey(0)
        elif key == ord('p'):
            cv2.imwrite('capture.png', frame)

        # FPS bookkeeping
        t_stop = time.perf_counter()
        frame_rate_calc = float(1.0 / max((t_stop - t_start), 1e-6))
        if len(frame_rate_buffer) >= fps_avg_len:
            frame_rate_buffer.pop(0)
        frame_rate_buffer.append(frame_rate_calc)
        avg_frame_rate = float(np.mean(frame_rate_buffer))

        frame_idx += 1

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    # Cleanup
    print(f'Average pipeline FPS: {avg_frame_rate:.2f}')
    print(f'Last detected people count: {last_object_count}')
    if cap is not None:
        if source_type == 'picamera':
            try:
                cap.stop()
            except Exception:
                pass
        else:
            try:
                cap.release()
            except Exception:
                pass
    if recorder is not None:
        try:
            recorder.release()
        except Exception:
            pass
    cv2.destroyAllWindows()
    conn.close()