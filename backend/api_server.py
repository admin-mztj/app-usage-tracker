from flask import Flask, jsonify, request
from flask_cors import CORS
import database
import logging
import os
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

app = Flask(__name__)
CORS(app)

@app.route('/api/usage/today', methods=['GET'])
def get_today_usage():
    logger.info("API request: /api/usage/today")
    sessions = database.get_today_usage()
    result = aggregate_usage(sessions)
    logger.info(f"Returned {len(result)} aggregated records for today")
    return jsonify(result)

@app.route('/api/usage/week', methods=['GET'])
def get_week_usage():
    logger.info("API request: /api/usage/week")
    dates = database.get_all_dates_in_week()
    sessions = database.get_week_usage()
    aggregated = aggregate_usage(sessions)
    logger.info(f"Returned {len(aggregated)} aggregated records for week")
    return jsonify({
        'dates': dates,
        'sessions': sessions,
        'aggregated': aggregated
    })

@app.route('/api/usage/month', methods=['GET'])
def get_month_usage():
    logger.info("API request: /api/usage/month")
    dates = database.get_all_dates_in_month()
    sessions = database.get_month_usage()
    aggregated = aggregate_usage(sessions)
    logger.info(f"Returned {len(aggregated)} aggregated records for month")
    return jsonify({
        'dates': dates,
        'sessions': sessions,
        'aggregated': aggregated
    })

@app.route('/api/usage/date/<date>', methods=['GET'])
def get_usage_by_date(date):
    logger.info(f"API request: /api/usage/date/{date}")
    sessions = database.get_usage_by_date(date)
    aggregated = aggregate_usage(sessions)
    logger.info(f"Returned {len(aggregated)} aggregated records for date {date}")
    return jsonify({
        'date': date,
        'sessions': sessions,
        'aggregated': aggregated
    })

@app.route('/api/usage/app/<app_name>/today/hourly', methods=['GET'])
def get_app_today_hourly(app_name):
    logger.info(f"API request: /api/usage/app/{app_name}/today/hourly")
    sessions = database.get_app_today_hourly(app_name)
    hourly_data = calculate_hourly_usage(sessions)
    logger.info(f"Returned hourly data for app: {app_name}")
    return jsonify(hourly_data)

@app.route('/api/usage/app/<app_name>/week/daily', methods=['GET'])
def get_app_week_daily(app_name):
    logger.info(f"API request: /api/usage/app/{app_name}/week/daily")
    sessions = database.get_app_week_hourly(app_name)
    daily_data = calculate_daily_usage(sessions, 'week')
    logger.info(f"Returned week daily data for app: {app_name}")
    return jsonify(daily_data)

@app.route('/api/usage/app/<app_name>/month/daily', methods=['GET'])
def get_app_month_daily(app_name):
    logger.info(f"API request: /api/usage/app/{app_name}/month/daily")
    sessions = database.get_app_month_hourly(app_name)
    daily_data = calculate_daily_usage(sessions, 'month')
    logger.info(f"Returned month daily data for app: {app_name}")
    return jsonify(daily_data)

def calculate_hourly_usage(sessions):
    now = datetime.now()
    hourly_usage = [0] * 24

    for session in sessions:
        start = parse_time(session['start_time'])
        end = parse_time(session['end_time']) if session['end_time'] else now

        if not start:
            continue

        if end < start:
            continue

        current_hour = start.hour
        current_time = start

        while current_time < end:
            next_hour_start = datetime(current_time.year, current_time.month, current_time.day, current_time.hour + 1) if current_time.hour < 23 else datetime(current_time.year, current_time.month, current_time.day, 23, 59, 59)

            if next_hour_start > end:
                next_hour_start = end

            minutes_in_hour = (next_hour_start - current_time).total_seconds() / 60
            hourly_usage[current_hour] += minutes_in_hour

            current_hour = (current_hour + 1) % 24
            current_time = next_hour_start

    for i in range(24):
        hourly_usage[i] = min(60, round(hourly_usage[i], 1))

    return hourly_usage

def calculate_daily_usage(sessions, period):
    now = datetime.now()
    daily_usage = {}
    
    if period == 'week':
        for i in range(7):
            date = now - timedelta(days=6 - i)
            date_str = date.strftime('%Y-%m-%d')
            daily_usage[date_str] = 0
    else:
        year = now.year
        month = now.month
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month + 1, 1) - timedelta(days=1) if month < 12 else datetime(year + 1, 1, 1) - timedelta(days=1)
        
        current_date = first_day
        while current_date <= last_day:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_usage[date_str] = 0
            current_date += timedelta(days=1)

    for session in sessions:
        start = parse_time(session['start_time'])
        end = parse_time(session['end_time']) if session['end_time'] else now

        if not start:
            continue

        if end < start:
            continue

        current_time = start
        while current_time < end:
            date_str = current_time.strftime('%Y-%m-%d')
            if date_str in daily_usage:
                next_day = datetime(current_time.year, current_time.month, current_time.day, 23, 59, 59) + timedelta(seconds=1)
                if next_day > end:
                    next_day = end
                
                seconds_in_day = (next_day - current_time).total_seconds()
                daily_usage[date_str] += seconds_in_day / 3600
                
                current_time = next_day
            else:
                break

    dates = list(daily_usage.keys())
    values = [round(daily_usage[d], 2) for d in dates]
    
    return {
        'dates': dates,
        'values': values
    }

def aggregate_usage(sessions):
    app_usage = {}
    now = datetime.now()

    for session in sessions:
        app_name = session['app_name']
        if app_name not in app_usage:
            app_usage[app_name] = {
                'app_name': app_name,
                'total_time': 0,
                'last_open': None,
                'last_close': None,
                'window_title': session.get('window_title', '')
            }

        start = parse_time(session['start_time'])
        if session['end_time']:
            end = parse_time(session['end_time'])
            if start and end:
                duration = (end - start).total_seconds()
                app_usage[app_name]['total_time'] += duration
        else:
            if start:
                duration = (now - start).total_seconds()
                app_usage[app_name]['total_time'] += duration

        if not app_usage[app_name]['last_open'] or session['start_time'] > app_usage[app_name]['last_open']:
            app_usage[app_name]['last_open'] = session['start_time']

        if session['end_time']:
            if not app_usage[app_name]['last_close'] or session['end_time'] > app_usage[app_name]['last_close']:
                app_usage[app_name]['last_close'] = session['end_time']

    sorted_apps = sorted(app_usage.values(), key=lambda x: x['last_open'] or '', reverse=True)
    return sorted_apps

def parse_time(time_str):
    try:
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except:
        return None

if __name__ == '__main__':
    logger.info("Starting API server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
