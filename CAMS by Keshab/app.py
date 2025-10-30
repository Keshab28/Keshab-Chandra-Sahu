from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "my_cams_secret_123"

DB_PATH = "cams.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# This makes 'username' available in ALL templates automatically
@app.context_processor
def inject_user():
    return dict(username=session.get("username"))

@app.route("/areas")
def areas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT area, people_count, status,
               datetime(updated_at, 'unixepoch', 'localtime') AS readable_time
        FROM area_status
        ORDER BY area
    """)
    rows = cursor.fetchall()
    conn.close()

    # convert to JSON-serializable format
    result = []
    for row in rows:
        result.append({
            "name": row["area"],
            "people_count": row["people_count"],
            "status": row["status"],
            "time_ago": row["readable_time"],
            "is_outdated": False
        })
    return jsonify(result)

@app.route("/update_status", methods=["POST"])
def update_status():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    area = data.get("area")
    count = data.get("people_count")
    timestamp = data.get("timestamp", int(time.time()))

    # Decide the area status
    if count == 0:
        status = "empty"
    elif count < 10:
        status = "open"
    elif count < 30:
        status = "busy"
    else:
        status = "closed"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO area_status (area, people_count, status, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(area) DO UPDATE SET
            people_count = excluded.people_count,
            status = excluded.status,
            updated_at = excluded.updated_at
    """, (area, count, status, timestamp))
    conn.commit()
    conn.close()

    print(f"✅ Received update ...")
    return jsonify({"message": "Data updated successfully"}), 200

# =======================
# 🔹 LOGIN FLOW
# =======================

@app.route("/")
def home():
    # if user not logged in → go to login page
    if "username" not in session:
        return redirect(url_for("login"))
    else:
        return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            session["is_new_user"] = False
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials! Please try again.")
    
    return render_template("login.html")


@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = generate_password_hash(request.form.get("password"))
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # now = datetime.datetime.now()

    conn = get_db_connection()
    existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if existing_user:
        conn.close()
        return render_template("login.html", error="Username already exists! Try logging in.")

    # create new user
    conn.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)", 
                 (username, password, created_at))
    conn.commit()
    conn.close()

    session["username"] = username
    session["is_new_user"] = True
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =======================
# 🔹 MAIN WEBSITE ROUTES
# =======================

@app.route("/index")
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM area_status ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()

    return render_template("index.html", areas=rows)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/credits")
def credits():
    return render_template("credits.html")


if __name__ == "__main__":
    # make sure the `users` table exists
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    app.run(debug=True)