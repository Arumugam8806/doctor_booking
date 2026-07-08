from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

db_path = os.path.abspath("appointments.db")

# --- Delete past appointments (date < today) ---
def delete_old_appointments():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    today = datetime.now().date()
    c.execute("DELETE FROM appointments WHERE date < ?", (today,))
    conn.commit()
    conn.close()

# Call after db_path is set
delete_old_appointments()

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d-%b-%Y'):
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime(format)
    except:
        return value

# -----------------------------------
# Create DB and Tables if Not Exist
# -----------------------------------
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''CREATE TABLE appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        phone TEXT,
        department TEXT,
        date TEXT,
        time TEXT
    )''')

    c.execute('''CREATE TABLE doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialization TEXT,
        time_slots TEXT
    )''')

    doctors = [
        ('Dr. Alphin', 'ENT Specialist', '10:00 AM - 1:00 PM'),
        ('Dr. Sumith', 'Dermatologist', '2:00 PM - 5:00 PM'),
        ('Dr. Arumugam', 'Cardiologist', '4:00 PM - 7:00 PM'),
        ('Dr. Diwakar', 'Physiotherapist', '10:00 AM - 2:00 PM')
    ]
    c.executemany("INSERT INTO doctors (name, specialization, time_slots) VALUES (?, ?, ?)", doctors)

    conn.commit()
    conn.close()
    print("✅ Database created successfully.")

# -----------------------------------
# Landing Page
# -----------------------------------
@app.route('/')
def landing():
    return render_template('landing.html')

# -----------------------------------
# Patient Page
# -----------------------------------
@app.route('/patient')
def patient():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT DISTINCT specialization FROM doctors")
    departments = [row[0] for row in c.fetchall()]

    c.execute("SELECT name, specialization, time_slots FROM doctors")
    doctors = c.fetchall()
    conn.close()

    return render_template('index.html', departments=departments, doctors=doctors)

# -----------------------------------
# Get available time slots
# -----------------------------------
def get_available_slots(department, date):
    max_slots = 10
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM appointments WHERE department=? AND date=?", (department, date))
    count = c.fetchone()[0]
    conn.close()
    return count < max_slots

# -----------------------------------
# Book Appointment
# -----------------------------------
@app.route('/book', methods=['POST'])
def book_appointment():
    name = request.form['name'].strip()
    age = request.form['age'].strip()
    phone = request.form['phone'].strip()
    department = request.form['department'].strip()
    date = request.form['date'].strip()
    time = request.form['time'].strip()

    # Phone validation
    if not (phone.isdigit() and len(phone) == 10):
        return "❌ Phone number must be exactly 10 digits."

    # Date validation
    try:
        appt_date = datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.now().date()
        max_date = today + timedelta(days=90)
        if appt_date < today or appt_date > max_date:
            return "❌ Appointment date must be within the next 3 months."
    except ValueError:
        return "❌ Invalid date format. Use YYYY-MM-DD."

    # Check available slots
    if not get_available_slots(department, date):
        return f"❌ No more available slots for {department} on {date}."

    # Insert into DB
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO appointments (name, age, phone, department, date, time) VALUES (?, ?, ?, ?, ?, ?)",
              (name, age, phone, department, date, time))
    conn.commit()

    c.execute("SELECT * FROM appointments ORDER BY id DESC LIMIT 1")
    latest_appointment = c.fetchone()
    conn.close()

    return render_template('success.html', appointment=latest_appointment)

# -----------------------------------
# Admin Login
# -----------------------------------
@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_auth', methods=['POST'])
def admin_auth():
    password = request.form.get('password')
    if password == 'admin@123':
        return redirect(url_for('view_appointments'))
    else:
        return "❌ Invalid password."

# -----------------------------------
# View Appointments Grouped
# -----------------------------------
def get_grouped_appointments():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, name, specialization, time_slots FROM doctors")
    doctors = c.fetchall()

    grouped = {}
    for doc in doctors:
        doc_id, name, specialization, time_slots = doc
        c.execute("SELECT * FROM appointments WHERE department=? ORDER BY date ASC, time ASC", (specialization,))
        appointments = c.fetchall()
        grouped[doc_id] = {
            'name': name,
            'specialization': specialization,
            'time_slots': time_slots,
            'appointments': appointments
        }
    conn.close()
    return grouped

@app.route('/appointments')
def view_appointments():
    grouped_appointments = get_grouped_appointments()
    return render_template('appointments.html', grouped_appointments=grouped_appointments)

# -----------------------------------
# Delete Appointment
# -----------------------------------
@app.route('/delete/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_appointments'))

# -----------------------------------
# Run Server
# -----------------------------------
if __name__ == '__main__':
    app.run(debug=True)
