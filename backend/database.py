import sqlite3
import os
import logging
from datetime import datetime, timedelta

# 配置日志
LOG_PATH = os.path.join(os.path.dirname(__file__), 'app_usage.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'app_usage.db')

def init_db():
    logger.info("Initializing database...")
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
    logger.info("Database initialized successfully")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def save_session(app_name, window_title, start_time, end_time=None):
    logger.info(f"Saving session: app={app_name}, title={window_title}, start={start_time}")
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
    logger.info(f"Session saved with ID: {session_id}")
    return session_id

def update_session_end_time(session_id, end_time):
    logger.info(f"Updating session end time: id={session_id}, end={end_time}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE app_sessions SET end_time = ? WHERE id = ?
    ''', (end_time, session_id))
    conn.commit()
    conn.close()
    logger.info(f"Session end time updated: id={session_id}")

def get_today_usage():
    logger.info("Querying today's usage...")
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, app_name, window_title, start_time, end_time
        FROM app_sessions
        WHERE date = ?
        ORDER BY start_time DESC
    ''', (today,))
    rows = cursor.fetchall()
    conn.close()
    result = [dict(row) for row in rows]
    logger.info(f"Found {len(result)} sessions for today")
    return result

def get_week_usage():
    logger.info("Querying week's usage...")
    today = datetime.now()
    weekday = today.weekday()
    week_start = (today - timedelta(days=weekday)).strftime('%Y-%m-%d')
    week_end = (today + timedelta(days=6-weekday)).strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, app_name, window_title, start_time, end_time, date
        FROM app_sessions
        WHERE date >= ? AND date <= ?
        ORDER BY date, start_time DESC
    ''', (week_start, week_end))
    rows = cursor.fetchall()
    conn.close()
    result = [dict(row) for row in rows]
    logger.info(f"Found {len(result)} sessions for week")
    return result

def get_month_usage():
    logger.info("Querying month's usage...")
    today = datetime.now()
    month_start = today.strftime('%Y-%m') + '-01'
    month_end = today.strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, app_name, window_title, start_time, end_time, date
        FROM app_sessions
        WHERE date >= ? AND date <= ?
        ORDER BY date, start_time DESC
    ''', (month_start, month_end))
    rows = cursor.fetchall()
    conn.close()
    result = [dict(row) for row in rows]
    logger.info(f"Found {len(result)} sessions for month")
    return result

def get_usage_by_date(date):
    logger.info(f"Querying usage for date: {date}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, app_name, window_title, start_time, end_time
        FROM app_sessions
        WHERE date = ?
        ORDER BY start_time DESC
    ''', (date,))
    rows = cursor.fetchall()
    conn.close()
    result = [dict(row) for row in rows]
    logger.info(f"Found {len(result)} sessions for date {date}")
    return result

def get_app_hourly_usage(app_name, date):
    logger.info(f"Querying hourly usage for app: {app_name}, date: {date}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT start_time, end_time
        FROM app_sessions
        WHERE app_name = ? AND date = ?
    ''', (app_name, date))
    rows = cursor.fetchall()
    conn.close()
    result = [dict(row) for row in rows]
    logger.info(f"Found {len(result)} hourly sessions for app {app_name}")
    return result

def get_app_today_hourly(app_name):
    today = datetime.now().strftime('%Y-%m-%d')
    return get_app_hourly_usage(app_name, today)

def get_app_week_hourly(app_name):
    logger.info(f"Querying week hourly usage for app: {app_name}")
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
    result = [dict(row) for row in rows]
    logger.info(f"Found {len(result)} week hourly sessions for app {app_name}")
    return result

def get_app_month_hourly(app_name):
    logger.info(f"Querying month hourly usage for app: {app_name}")
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
    result = [dict(row) for row in rows]
    logger.info(f"Found {len(result)} month hourly sessions for app {app_name}")
    return result

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
