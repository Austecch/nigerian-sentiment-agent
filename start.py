import os
import subprocess
import sys
import time

RAILWAY_PORT = int(os.environ.get("PORT", 8000))

# Streamlit goes on the Railway-exposed port
dashboard = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run",
    "dashboard/app.py",
    "--server.port", str(RAILWAY_PORT),
    "--server.address", "0.0.0.0",
])

# FastAPI on a fixed internal port (dashboard calls it at 127.0.0.1:8000)
time.sleep(1)
backend = subprocess.Popen([
    sys.executable, "-m", "uvicorn",
    "api.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
])

dashboard.wait()
backend.wait()
