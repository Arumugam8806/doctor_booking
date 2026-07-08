import sqlite3

conn = sqlite3.connect('appointments.db')
c = conn.cursor()

c.execute("SELECT * FROM appointments")
rows = c.fetchall()

if rows:
    print("Appointments found:")
    for row in rows:
        print(row)
else:
    print("No appointments found.")

conn.close()
