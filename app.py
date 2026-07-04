from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'hospital_secret_2026'

def init_db():
    conn = sqlite3.connect('hospital.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'staff'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        diagnosis TEXT,
        doctor TEXT,
        date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        doctor TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )''')
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    except:
        pass
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('hospital.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        flash('بيانات خاطئة!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    total_patients = conn.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
    total_appointments = conn.execute('SELECT COUNT(*) FROM appointments').fetchone()[0]
    conn.close()
    return render_template('dashboard.html', total_patients=total_patients, total_appointments=total_appointments)

@app.route('/patients')
def patients():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    patients = conn.execute('SELECT * FROM patients').fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)

@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        conn = get_db()
        conn.execute('INSERT INTO patients (name, age, gender, phone, diagnosis, doctor, date) VALUES (?,?,?,?,?,?,?)',
            (request.form['name'], request.form['age'], request.form['gender'],
             request.form['phone'], request.form['diagnosis'], request.form['doctor'],
             datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        flash('تمت إضافة المريض!')
        return redirect(url_for('patients'))
    return render_template('add_patient.html')

@app.route('/patients/delete/<int:id>')
def delete_patient(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM patients WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('patients'))

@app.route('/appointments')
def appointments():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    appointments = conn.execute('SELECT * FROM appointments').fetchall()
    conn.close()
    return render_template('appointments.html', appointments=appointments)

@app.route('/appointments/add', methods=['GET', 'POST'])
def add_appointment():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        conn = get_db()
        conn.execute('INSERT INTO appointments (patient_name, doctor, date, time) VALUES (?,?,?,?)',
            (request.form['patient_name'], request.form['doctor'],
             request.form['date'], request.form['time']))
        conn.commit()
        conn.close()
        flash('تمت إضافة الموعد!')
        return redirect(url_for('appointments'))
    return render_template('add_appointment.html')

if __name__ == '__main__':
    app.run(debug=True)
