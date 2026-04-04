import subprocess, sys, time, os

print("Starting Smart Scout — localhost demo")
print("=" * 40)

# Failsafe: Ensure we use the virtual environment's python even if the user ran 'python run.py' globally
PYTHON_BIN = "venv/Scripts/python" if os.path.exists("venv/Scripts/python.exe") else sys.executable

processes = []

print("[1/4] Initializing database...")
subprocess.run([PYTHON_BIN, "-m", "backend.seed"])

print("[2/4] Starting FastAPI on localhost:8000...")
p1 = subprocess.Popen([PYTHON_BIN, "-m", "uvicorn",
                        "backend.api:app", "--port", "8000"])
processes.append(p1)
time.sleep(2)

print("[3/4] Starting background crawl scheduler...")
p2 = subprocess.Popen([PYTHON_BIN, "-m", "backend.scheduler"])
processes.append(p2)
time.sleep(1)

print("[4/4] Starting Streamlit dashboard on localhost:8501...")
print("\nOpen: http://localhost:8501\nPress Ctrl+C to stop all services.\n")
p3 = subprocess.Popen([PYTHON_BIN, "-m", "streamlit",
                        "run", "dashboard/app.py"])
processes.append(p3)

try:
    p3.wait()
except KeyboardInterrupt:
    print("\nShutting down...")
    for p in processes:
        p.terminate()
