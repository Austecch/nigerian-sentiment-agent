import os
import subprocess
import sys
import time

PORT = int(os.environ.get("PORT", 8000))

# Start FastAPI backend in background
backend = subprocess.Popen([
    sys.executable, "-m", "uvicorn",
    "api.main:app",
    "--host", "0.0.0.0",
    "--port", str(PORT),
])

# Wait for backend to start
time.sleep(3)

# Start Streamlit dashboard
dashboard_port = 8501 if PORT != 8501 else 8502
dashboard = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run",
    "dashboard/app.py",
    "--server.port", str(dashboard_port),
    "--server.address", "0.0.0.0",
])

# Wait for both
backend.wait()
dashboard.wait()
