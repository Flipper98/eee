# app.py
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import sqlite3
import requests
import icalendar
import os

app = Flask(__name__)


# Функция для подключения к базе данных
def get_db():
    db = sqlite3.connect('university.db')
    db.row_factory = sqlite3.Row
    return db


# Инициализация базы данных
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# Функция для загрузки расписания
def fetch_schedule():
    url = "https://bonchbot.ru/export/7cfe3d2a765f437a9d0f805778f7072c"
    response = requests.get(url)
    cal = icalendar.Calendar.from_ical(response.text)


    events = []
    for event in cal.walk('vevent'):
        events.append({
            'summary': str(event.get('summary')),
            'description': str(event.get('description')),
            'location': str(event.get('location')),
            'start': event.get('dtstart').dt,
            'end': event.get('dtend').dt
        })
    return events


# Маршруты
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/schedule')
def get_schedule():
    try:
        events = fetch_schedule()
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/students', methods=['GET', 'POST'])
def handle_students():
    db = get_db()
    if request.method == 'POST':
        data = request.json
        db.execute('INSERT INTO students (name, email) VALUES (?, ?)',
                   [data['name'], data['email']])
        db.commit()
        return jsonify({'status': 'success'})

    students = db.execute('SELECT * FROM students').fetchall()
    return jsonify([dict(student) for student in students])


@app.route('/api/subjects', methods=['GET', 'POST'])
def handle_subjects():
    db = get_db()
    if request.method == 'POST':
        data = request.json
        db.execute('INSERT INTO subjects (name, professor, description) VALUES (?, ?, ?)',
                   [data['name'], data['professor'], data['description']])
        db.commit()
        return jsonify({'status': 'success'})

    subjects = db.execute('SELECT * FROM subjects').fetchall()
    return jsonify([dict(subject) for subject in subjects])


if __name__ == '__main__':
    if not os.path.exists('university.db'):
        init_db()
    app.run(debug=True)