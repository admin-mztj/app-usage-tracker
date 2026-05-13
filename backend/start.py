import subprocess
import sys
import os

def main():
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    print("Starting window tracker service...")
    tracker_process = subprocess.Popen(
        [sys.executable, os.path.join(backend_dir, 'window_tracker.py')],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

    print("Starting API server...")
    api_process = subprocess.Popen(
        [sys.executable, os.path.join(backend_dir, 'api_server.py')],
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

if __name__ == '__main__':
    main()
