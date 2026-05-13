import subprocess
import sys
import os
import time
import signal

PYTHON_PATH = 'e:\\anaconda3\\python.exe'

def main():
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

    processes = []

    try:
        print("=" * 50)
        print("应用使用时间追踪器")
        print("=" * 50)

        print("\n[1/3] 启动窗口追踪服务...")
        tracker_process = subprocess.Popen(
            [PYTHON_PATH, os.path.join(backend_dir, 'window_tracker.py')],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(('tracker', tracker_process))
        time.sleep(1)
        print("    ✓ 窗口追踪服务已启动")

        print("\n[2/3] 启动 API 服务器...")
        api_process = subprocess.Popen(
            [PYTHON_PATH, os.path.join(backend_dir, 'api_server.py')],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(('api', api_process))
        time.sleep(2)
        print("    ✓ API 服务已启动 (http://127.0.0.1:5000)")

        print("\n[3/3] 启动前端服务器...")
        frontend_process = subprocess.Popen(
            [PYTHON_PATH, '-m', 'http.server', '8000'],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(('frontend', frontend_process))
        time.sleep(1)
        print("    ✓ 前端服务已启动 (http://127.0.0.1:8000)")

        print("\n" + "=" * 50)
        print("所有服务已启动！")
        print("  - 窗口追踪: 运行中")
        print("  - API 服务: http://127.0.0.1:5000")
        print("  - 前端界面: http://127.0.0.1:8000")
        print("=" * 50)
        print("\n按 Ctrl+C 停止所有服务")

        for name, p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\n\n正在停止所有服务...")
        for name, p in processes:
            try:
                p.terminate()
                p.wait(timeout=3)
                print(f"  ✓ {name} 已停止")
            except:
                p.kill()
                print(f"  ✓ {name} 已强制终止")
        print("\n所有服务已停止。")

if __name__ == '__main__':
    main()
