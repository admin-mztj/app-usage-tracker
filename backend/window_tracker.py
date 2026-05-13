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

    def track_windows(self):
        pythoncom.CoInitialize()
        while self.tracking:
            try:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                fg_hwnd = win32gui.GetForegroundWindow()

                if fg_hwnd:
                    info = self.get_window_info(fg_hwnd)
                    if info:
                        if fg_hwnd != self.current_fg_hwnd:
                            if self.current_fg_hwnd and self.current_fg_hwnd in self.window_sessions:
                                database.update_session_end_time(self.window_sessions[self.current_fg_hwnd], now)

                            session_id = database.save_session(
                                info['exe_name'],
                                info['title'],
                                now
                            )
                            self.window_sessions[fg_hwnd] = session_id
                            self.current_fg_hwnd = fg_hwnd

            except Exception as e:
                print(f"Error in tracking: {e}")

            time.sleep(1)
        pythoncom.CoUninitialize()

    def periodic_check(self):
        while self.tracking:
            try:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for hwnd in list(self.window_sessions.keys()):
                    if not self.is_window_alive(hwnd):
                        database.update_session_end_time(self.window_sessions[hwnd], now)
                        del self.window_sessions[hwnd]
                        if self.current_fg_hwnd == hwnd:
                            self.current_fg_hwnd = None
            except Exception as e:
                print(f"Error in periodic check: {e}")
            time.sleep(5)

    def start(self):
        self.tracking = True
        self.current_fg_hwnd = None
        self.window_sessions = {}
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
