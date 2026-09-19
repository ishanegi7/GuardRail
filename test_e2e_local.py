import subprocess
import time
import httpx
import os
import sys

def run_servers():
    env = os.environ.copy()
    
    # Start Demo API
    print("Starting demo-api on 8080...")
    demo_api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8080"],
        cwd="apps/demo-api",
        env=env
    )
    
    # Start GuardRail API
    print("Starting guardrail-api on 8000...")
    env["DEMO_API_URL"] = "http://127.0.0.1:8080"
    env["SANDBOX_DIR"] = os.path.abspath("apps/demo-api")
    import tempfile
    env["TARGET_SANDBOX_DIR"] = os.path.join(tempfile.gettempdir(), "guardrail-sandbox-test")
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd="apps/api",
        env=env
    )
    
    return demo_api, api

def wait_for_services():
    print("Waiting for services to be ready...")
    ready = False
    for _ in range(30):
        try:
            r1 = httpx.get("http://127.0.0.1:8080/")
            r2 = httpx.get("http://127.0.0.1:8000/api/projects")
            if r1.status_code == 200 and r2.status_code == 200:
                ready = True
                break
        except Exception:
            pass
        time.sleep(1)
    if not ready:
        raise Exception("Services failed to start")

def test_workflow():
    print("Triggering Scan...")
    r = httpx.get("http://127.0.0.1:8000/api/projects")
    projects = r.json()
    if not projects:
        raise Exception("No projects found")
    proj_id = projects[0]["id"]
    
    r = httpx.post("http://127.0.0.1:8000/api/scans", json={"project_id": proj_id})
    scan = r.json()
    scan_id = scan["id"]
    
    print(f"Waiting for scan {scan_id} to complete...")
    for _ in range(20):
        r = httpx.get(f"http://127.0.0.1:8000/api/scans")
        scans = r.json()
        scan = next(s for s in scans if s["id"] == scan_id)
        if scan["status"] in ["completed", "failed"]:
            break
        time.sleep(1)
        
    if scan["status"] != "completed":
        raise Exception(f"Scan failed to complete. Final status: {scan['status']}")
        
    r = httpx.get(f"http://127.0.0.1:8000/api/findings?scan_id={scan_id}")
    findings = r.json()
    print(f"Found {len(findings)} findings.")
    
    bola = next((f for f in findings if "BOLA" in f["vulnerability_type"]), None)
    if not bola:
        raise Exception("BOLA finding not generated!")
    print(f"BOLA finding found: {bola['id']}")
    
    print("Generating Patch...")
    r = httpx.post(f"http://127.0.0.1:8000/api/findings/{bola['id']}/generate-patch", timeout=30.0)
    finding = r.json()
    if finding["patch_status"] != "generated":
        raise Exception(f"Failed to generate patch: {finding['patch_status']}")
        
    print("Verifying Patch...")
    r = httpx.post(f"http://127.0.0.1:8000/api/findings/{bola['id']}/verify-patch", timeout=30.0)
    finding = r.json()
    if finding["patch_status"] != "verified":
        raise Exception(f"Failed to verify patch. Status: {finding['patch_status']}")
        
    print("E2E WORKFLOW SUCCESSFUL!")

if __name__ == "__main__":
    demo_api, api = run_servers()
    try:
        wait_for_services()
        test_workflow()
    finally:
        print("Terminating servers...")
        demo_api.terminate()
        api.terminate()
