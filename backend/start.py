import subprocess
import sys
import os
import winreg

def get_script_path():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(backend_dir, 'window_tracker.py')

def get_api_path():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(backend_dir, 'api_server.py')

def add_to_startup():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "AppUsageTracker"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        script_path = get_script_path()
        command = f'"{sys.executable}" "{script_path}" --background'
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        print(f"✅ 已添加到开机自启动: {app_name}")
        return True
    except WindowsError as e:
        print(f"❌ 添加开机自启动失败: {e}")
        return False

def remove_from_startup():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "AppUsageTracker"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, app_name)
        winreg.CloseKey(key)
        print(f"✅ 已从开机自启动移除: {app_name}")
        return True
    except WindowsError:
        print(f"ℹ️ 开机自启动项不存在或已移除")
        return True

def is_in_startup():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "AppUsageTracker"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, app_name)
        winreg.CloseKey(key)
        return True
    except WindowsError:
        return False

def start_services():
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    print("Starting window tracker service...")
    tracker_process = subprocess.Popen(
        [sys.executable, get_script_path()],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

    print("Starting API server...")
    api_process = subprocess.Popen(
        [sys.executable, get_api_path()],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

    print("Services started!")
    print("API Server: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop all services")

    try:
        tracker_process.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        tracker_process.terminate()
        api_process.terminate()

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--add-startup":
            add_to_startup()
            return
        elif sys.argv[1] == "--remove-startup":
            remove_from_startup()
            return
        elif sys.argv[1] == "--check-startup":
            if is_in_startup():
                print("✅ 已开启开机自启动")
            else:
                print("❌ 未开启开机自启动")
            return
        elif sys.argv[1] == "--background":
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            tracker_process = subprocess.Popen(
                [sys.executable, get_script_path()],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            api_process = subprocess.Popen(
                [sys.executable, get_api_path()],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            tracker_process.wait()
            return

    if is_in_startup():
        print("📌 开机自启动: 已开启")
    else:
        print("📌 开机自启动: 未开启")

    print("\n使用说明:")
    print("  python start.py                    - 启动服务")
    print("  python start.py --add-startup     - 开启开机自启动")
    print("  python start.py --remove-startup  - 关闭开机自启动")
    print("  python start.py --check-startup   - 检查开机自启动状态")

    start_services()

if __name__ == '__main__':
    main()
