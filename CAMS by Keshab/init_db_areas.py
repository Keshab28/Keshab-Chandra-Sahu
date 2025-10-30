import sqlite3
import os

areas = [
    ("auditorium", "Auditorium"),
    ("canteen", "Canteen"),
    ("computer_lab", "Computer Lab"),
    ("hod_room", "HOD Room"),
    ("library", "Library"),
    ("sports_complex", "Sports Complex")
]

for shortname, pretty in areas:
    db_filename = f"{shortname}.db"   # e.g., auditorium.db

    if os.path.exists(db_filename):
        print(f"⚠️ Existing database '{db_filename}' found. Deleting it...")
        os.remove(db_filename)
    else:
        print("✅ No existing database found. Creating a new one...")

    # create file + table
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            people_count INTEGER,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"Initialized {db_filename}")