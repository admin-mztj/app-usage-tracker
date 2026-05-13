import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'app_usage.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            window_title TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_session(app_name, window_title, start_time, end_time=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    date = start_time[:10]
    cursor.execute('''
        INSERT INTO app_sessions (app_name, window_title, start_time, end_time, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (app_name, window_title, start_time, end_time, date))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def update_session_end_time(session_id, end_time):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE app_sessions SET end_time = ? WHERE id = ?
    ''', (end_time, session_id))
    conn.commit()
    conn.close()

def get_today_usage():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT app_name, window_title, start_time, end_time
        FROM app_sessions
        WHERE date = ?
        ORDER BY start_time DESC
    ''', (today,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_week_usage():
    today = datetime.now()
    weekday = today.weekday()
    week_start = (today - timedelta(days=weekday)).strftime('%Y-%m-%d')
    week_end = (today + timedelta(days=6-weekday)).strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT app_name, window_title, start_time, end_time, date
        FROM app_sessions
        WHERE date >= ? AND date <= ?
        ORDER BY date, start_time DESC
    ''', (week_start, week_end))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_month_usage():
    today = datetime.now()
    month_start = today.strftime('%Y-%m') + '-01'
    month_end = today.strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT app_name, window_title, start_time, end_time, date
        FROM app_sessions
        WHERE date >= ? AND date <= ?
        ORDER BY date, start_time DESC
    ''', (month_start, month_end))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_usage_by_date(date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT app_name, window_title, start_time, end_time
        FROM app_sessions
        WHERE date = ?
        ORDER BY start_time DESC
    ''', (date,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_app_hourly_usage(app_name, date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT start_time, end_time
        FROM app_sessions
        WHERE app_name = ? AND date = ?
    ''', (app_name, date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_app_today_hourly(app_name):
    today = datetime.now().strftime('%Y-%m-%d')
    return get_app_hourly_usage(app_name, today)

def get_app_week_hourly(app_name):
    today = datetime.now()
    weekday = today.weekday()
    week_start = (today - timedelta(days=weekday)).strftime('%Y-%m-%d')
    week_end = (today + timedelta(days=6-weekday)).strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT start_time, end_time, date
        FROM app_sessions
        WHERE app_name = ? AND date >= ? AND date <= ?
    ''', (app_name, week_start, week_end))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_app_month_hourly(app_name):
    today = datetime.now()
    month_start = today.strftime('%Y-%m') + '-01'
    month_end = today.strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT start_time, end_time, date
        FROM app_sessions
        WHERE app_name = ? AND date >= ? AND date <= ?
    ''', (app_name, month_start, month_end))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_dates_in_week():
    today = datetime.now()
    weekday = today.weekday()
    dates = []
    for i in range(7):
        date = (today - timedelta(days=weekday-i)).strftime('%Y-%m-%d')
        dates.append(date)
    return dates

def get_all_dates_in_month():
    today = datetime.now()
    year = today.year
    month = today.month
    if month == 12:
        next_month = datetime(year+1, 1, 1)
    else:
        next_month = datetime(year, month+1, 1)
    last_day = (next_month - timedelta(days=1)).day

    dates = []
    for day in range(1, last_day+1):
        date = today.strftime('%Y-%m') + f'-{day:02d}'
        dates.append(date)
    return dates

init_db()
