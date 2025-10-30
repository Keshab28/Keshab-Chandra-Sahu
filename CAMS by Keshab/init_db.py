import time
import sqlite3
from datetime import datetime
# import datetime
from werkzeug.security import generate_password_hash
import os

if os.path.exists("cams.db"):
    print(f"⚠️ Existing database '{"cams.db"}' found. Deleting it...")
    os.remove("cams.db")
else:
    print("✅ No existing database found. Creating a new one...")

conn = sqlite3.connect('cams.db')
c = conn.cursor()

# Create areas table
c.execute('''CREATE TABLE area_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT UNIQUE,
            people_count INTEGER,
            status TEXT,
            updated_at INTEGER
        );''')

# Create users table
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
              password TEXT NOT NULL,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

# Insert sample areas
sample_areas = [
    ('Library', 28, 'busy', int(time.time())),
    ('Canteen', 21, 'open', int(time.time())),
    ('HOD Room', 32, 'empty', int(time.time())),
    ('Computer Lab', 12, 'closed', int(time.time())),
    ('Auditorium', 0, 'open', int(time.time())),
    ('Sports Complex', 5, 'closed', int(time.time()))
]

c.executemany('INSERT INTO area_status (area, people_count, status, updated_at) VALUES (?, ?, ?, ?)', 
              sample_areas)

# Create a test user
test_password = generate_password_hash('password123')
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
c.execute('INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
          ('testuser', test_password, created_at))

conn.commit()
conn.close()

print("Database initialized successfully!")