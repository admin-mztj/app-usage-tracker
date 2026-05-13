import time
import threading
import pythoncom
from datetime import datetime
from win32 import win32gui
from win32 import win32process
from win32 import win32api
import win32con
import database

class WindowTracker:
    def __init__(self):
        self.tracking = False
        self.current_fg_hwnd = None
        self.window_sessions = {}
        self.app_sessions = {}

    def get_window_info(self, hwnd):
        try:
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return None

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
                exe_name = win32process.GetModuleFileNameEx(handle, 0)
                exe_name = exe_name.split('\\')[-1] if exe_name else 'Unknown'
                win32api.CloseHandle(handle)
            except:
                exe_name = 'Unknown'

            return {
                'hwnd': hwnd,
                'title': title,
                'exe_name': exe_name
            }
        except:
            return None

    def is_window_alive(self, hwnd):
        try:
            return win32gui.IsWindow(hwnd)
        except:
            return False

    def get_process_name(self, hwnd):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            exe_name = win32process.GetModuleFileNameEx(handle, 0)
            exe_name = exe_name.split('\\')[-1] if exe_name else 'Unknown'
            win32api.CloseHandle(handle)
            return exe_name
        except:
            return 'Unknown'

    def is_process_running(self, exe_name):
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if proc.name().lower() == exe_name.lower():
                    return True
            return False
        except:
            return True

    def restore_sessions(self):
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            sessions = database.get_today_usage()
            for session in sessions:
                if not session['end_time']:
                    app_name = session['app_name']
                    if app_name not in self.app_sessions:
                        self.app_sessions[app_name] = {
                            'session_id': session['id'],
                            'start_time': session['start_time'],
                            'window_title': session.get('window_title', '')
                        }
            print(f"Restored {len(self.app_sessions)} active sessions")
        except Exception as e:
            print(f"Error restoring sessions: {e}")

    def track_windows(self):
        pythoncom.CoInitialize()
        while self.tracking:
            try:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                fg_hwnd = win32gui.GetForegroundWindow()

                if fg_hwnd:
                    info = self.get_window_info(fg_hwnd)
                    if info:
                        app_name = info['exe_name']
                        
                        if fg_hwnd != self.current_fg_hwnd:
                            if self.current_fg_hwnd:
                                old_app_name = self.get_process_name(self.current_fg_hwnd)
                                if old_app_name in self.app_sessions:
                                    database.update_session_end_time(self.app_sessions[old_app_name]['session_id'], now)
                                    del self.app_sessions[old_app_name]

                            if app_name not in self.app_sessions:
                                session_id = database.save_session(
                                    app_name,
                                    info['title'],
                                    now
                                )
                                self.app_sessions[app_name] = {
                                    'session_id': session_id,
                                    'start_time': now,
                                    'window_title': info['title']
                                }
                            
                            self.current_fg_hwnd = fg_hwnd
                            if app_name in self.app_sessions:
                                self.app_sessions[app_name]['window_title'] = info['title']

            except Exception as e:
                print(f"Error in tracking: {e}")

            time.sleep(1)
        pythoncom.CoUninitialize()

    def periodic_check(self):
        while self.tracking:
            try:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for app_name in list(self.app_sessions.keys()):
                    if not self.is_process_running(app_name):
                        database.update_session_end_time(self.app_sessions[app_name]['session_id'], now)
                        del self.app_sessions[app_name]
                        if self.current_fg_hwnd:
                            current_app = self.get_process_name(self.current_fg_hwnd)
                            if current_app == app_name:
                                self.current_fg_hwnd = None
            except Exception as e:
                print(f"Error in periodic check: {e}")
            time.sleep(5)

    def start(self):
        self.tracking = True
        self.current_fg_hwnd = None
        self.window_sessions = {}
        self.app_sessions = {}
        
        self.restore_sessions()
        
        self.track_thread = threading.Thread(target=self.track_windows, daemon=True)
        self.check_thread = threading.Thread(target=self.periodic_check, daemon=True)
        self.track_thread.start()
        self.check_thread.start()

    def stop(self):
        self.tracking = False
        if hasattr(self, 'track_thread'):
            self.track_thread.join(timeout=2)
        if hasattr(self, 'check_thread'):
            self.check_thread.join(timeout=2)

if __name__ == '__main__':
    tracker = WindowTracker()
    tracker.start()
    print("Window tracker started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tracker.stop()
        print("Window tracker stopped.")
