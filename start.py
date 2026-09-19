import subprocess
import os
import sys

env = os.environ.copy()

print("Starting apps/demo-api on port 8080...")
demo_api = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--port", "8080"],
    cwd="apps/demo-api",
    env=env
)

print("Starting apps/api on port 8000...")
env["DEMO_API_URL"] = "http://127.0.0.1:8080"
env["SANDBOX_DIR"] = os.path.abspath("apps/demo-api")
import tempfile
env["TARGET_SANDBOX_DIR"] = os.path.join(tempfile.gettempdir(), "guardrail-sandbox")
api = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
    cwd="apps/api",
    env=env
)

print("Starting apps/web on port 3000...")
web = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd="apps/web",
    shell=True
)

print("\n--- All services started ---")
print("Web UI: http://localhost:3000")
print("Press Ctrl+C to stop.")

try:
    demo_api.wait()
except KeyboardInterrupt:
    print("Stopping services...")
    demo_api.terminate()
    api.terminate()
    web.terminate()
