import sqlite3
import os

# Get absolute path to the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "appointments.db")

# Connect to the database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create the doctors table
c.execute('''
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    time_slots TEXT NOT NULL
)
''')

# Create the appointments table
c.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    phone TEXT NOT NULL CHECK(length(phone) = 10),
    department TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL
)
''')

# Insert sample doctors if the table is empty
c.execute("SELECT COUNT(*) FROM doctors")
if c.fetchone()[0] == 0:
    doctors = [
        ('Dr. Alphin', 'ENT Specialist', '10:00 AM - 1:00 PM'),
        ('Dr. Sumith', 'Dermatologist', '2:00 PM - 5:00 PM'),
        ('Dr. Arumugam', 'Cardiologist', '4:00 PM - 7:00 PM'),
        ('Dr. Diwakar', 'Physiotherapist', '10:00 AM - 2:00 PM'),
    ]
    c.executemany("INSERT INTO doctors (name, specialization, time_slots) VALUES (?, ?, ?)", doctors)

conn.commit()
conn.close()

print("✅ Database setup complete with doctor and appointment tables.")

