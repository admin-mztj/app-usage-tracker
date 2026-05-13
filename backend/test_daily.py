from flask import Flask, jsonify, request
from flask_cors import CORS
import database
from datetime import datetime, timedelta
import sys

app = Flask(__name__)
CORS(app)

print("Testing database functions...")

try:
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Today: {today}")
    
    sessions = database.get_today_usage()
    print(f"Today's sessions: {len(sessions)}")
    
    if sessions:
        app_name = sessions[0]['app_name']
        print(f"Testing app: {app_name}")
        
        weekly = database.get_app_week_hourly(app_name)
        print(f"Weekly sessions: {len(weekly)}")
        
        monthly = database.get_app_month_hourly(app_name)
        print(f"Monthly sessions: {len(monthly)}")
        
        print("\nTesting calculate_daily_usage...")
        print("Weekly calculation:")
        
        now = datetime.now()
        daily_usage = {}
        
        for i in range(7):
            date = now - timedelta(days=6-i)
            date_str = date.strftime('%Y-%m-%d')
            daily_usage[date_str] = 0
            
        print(f"Daily usage keys: {list(daily_usage.keys())}")
        
        for session in weekly:
            start = datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S')
            if session['end_time']:
                end = datetime.strptime(session['end_time'], '%Y-%m-%d %H:%M:%S')
            else:
                end = now
                
            print(f"Session: {start} to {end}")
            
            current_time = start
            while current_time < end:
                date_str = current_time.strftime('%Y-%m-%d')
                if date_str in daily_usage:
                    next_day = datetime(current_time.year, current_time.month, current_time.day, 23, 59, 59) + timedelta(seconds=1)
                    if next_day > end:
                        next_day = end
                    
                    seconds_in_day = (next_day - current_time).total_seconds()
                    daily_usage[date_str] += seconds_in_day / 3600
                    print(f"  Adding to {date_str}: {seconds_in_day / 3600:.2f} hours")
                    
                    current_time = next_day
                else:
                    break
        
        dates = list(daily_usage.keys())
        values = [round(daily_usage[d], 2) for d in dates]
        
        print(f"\nFinal result:")
        print(f"Dates: {dates}")
        print(f"Values: {values}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTest successful!")
