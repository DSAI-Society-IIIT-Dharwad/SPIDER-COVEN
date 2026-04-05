import subprocess, sys, time, os

print("Starting Smart Scout — localhost demo")
print("=" * 40)

processes = []

# 1. Seed DB if empty
print("[1/4] Initializing database...")
subprocess.run([sys.executable, "backend/seed.py"])

# 2. FastAPI
print("[2/4] Starting FastAPI on localhost:8000...")
p1 = subprocess.Popen([sys.executable, "-m", "uvicorn",
                        "backend.api:app", "--reload", "--port", "8000"])
processes.append(p1)
time.sleep(2)

# 3. Scheduler
print("[3/4] Starting background crawl scheduler...")
p2 = subprocess.Popen([sys.executable, "backend/scheduler.py"])
processes.append(p2)
time.sleep(1)

# 4. Streamlit
print("[4/4] Starting Streamlit dashboard on localhost:8501...")
print("\nOpen: http://localhost:8501\nPress Ctrl+C to stop all services.\n")
p3 = subprocess.Popen([sys.executable, "-m", "streamlit",
                        "run", "dashboard/app.py"])
processes.append(p3)

try:
    p3.wait()
except KeyboardInterrupt:
    print("\nShutting down...")
    for p in processes:
        p.terminate()
