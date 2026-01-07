import sys
import os
import threading
import time
import uvicorn
import logging

# Only modify path if not frozen (i.e. running from source)
if not getattr(sys, 'frozen', False):
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Now we can import.
# Note: PyInstaller should bundle 'src' package if configured correctly.
try:
    from src.backend.main import app
except ImportError:
    # If that failed, maybe it was bundled as 'backend' directly?
    try:
        from backend.main import app
    except ImportError as e:
        print(f"Failed to import app: {e}")
        # print(f"sys.path: {sys.path}")
        sys.exit(1)

def start_server():
    # Run uvicorn programmatically
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def main():
    print("Starting AutoShavian...")

    # Patch backend to serve frontend assets
    from fastapi.staticfiles import StaticFiles

    if hasattr(sys, '_MEIPASS'):
        frontend_dir = os.path.join(sys._MEIPASS, 'frontend')
    else:
        frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')

    print(f"Serving frontend from: {frontend_dir}")

    if os.path.exists(frontend_dir):
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
    else:
        print("Warning: Frontend directory not found!")

    # Start server
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Wait for server
    time.sleep(2)

    print("AutoShavian is running. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
