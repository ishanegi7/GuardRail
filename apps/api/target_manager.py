import os
import shutil
import subprocess
import time
import httpx

class TargetManager:
    def __init__(self, source_dir: str = None, sandbox_dir: str = None):
        self.source_dir = source_dir or os.environ.get("TARGET_SOURCE_DIR", os.environ.get("SANDBOX_DIR", "/sandbox/demo-api"))
        self.sandbox_dir = sandbox_dir or os.environ.get("TARGET_SANDBOX_DIR", "/tmp/sandbox/demo-api")
        self.port = 8081
        self.process = None
        self.original_source_dir = self.source_dir

    def create_isolated_workspace(self):
        # Create a fresh copy of the demo target
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)
        # Avoid copying __pycache__, data, etc if we want it clean, but for simplicity copy all
        shutil.copytree(self.original_source_dir, self.sandbox_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', 'data', '*.pyc'))
        
        # Make sure data dir exists in sandbox
        os.makedirs(os.path.join(self.sandbox_dir, "data"), exist_ok=True)
        
    def start_target(self):
        if self.process:
            self.stop_target()
            
        print("Starting isolated demo target...")
        # Start uvicorn process
        env = os.environ.copy()
        env["DATABASE_URL"] = "sqlite:///./data/demo.db" # Local to sandbox
        
        # Find path to uvicorn inside virtualenv if running locally, or system path
        self.process = subprocess.Popen(
            ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(self.port)],
            cwd=self.sandbox_dir,
            env=env,
            stdout=subprocess.DEVNULL, # or log to file
            stderr=subprocess.DEVNULL
        )
        self.wait_for_health()

    def stop_target(self):
        if self.process:
            print("Stopping demo target...")
            self.process.terminate()
            self.process.wait()
            self.process = None
            
    def restart_target(self):
        self.stop_target()
        self.start_target()
        
    def wait_for_health(self):
        url = self.get_target_url()
        for _ in range(30):
            try:
                res = httpx.get(f"{url}/")
                if res.status_code == 200:
                    return True
            except:
                pass
            time.sleep(0.5)
        raise Exception("Target failed to start within timeout.")
        
    def get_target_url(self):
        return f"http://127.0.0.1:{self.port}"
        
    def apply_patch(self, diff_content: str, file_path_relative: str):
        if ".." in diff_content or "\n--- /" in diff_content or "\n+++ /" in diff_content:
            raise Exception("Potentially malicious patch detected (path traversal or absolute path).")
            
        patch_path = os.path.join(self.sandbox_dir, "fix.patch")
        with open(patch_path, "w") as f:
            f.write(diff_content)
            
        import shutil
        if not shutil.which("patch"):
            raise Exception("The 'patch' command is not available on this system.")

        # Run patch -p0 < fix.patch
        with open(patch_path, "r") as f:
            result = subprocess.run(["patch", "-p0"], stdin=f, capture_output=True, text=True, cwd=self.sandbox_dir)
        
        if result.returncode != 0:
            print(f"Patch failed. STDOUT: {result.stdout} STDERR: {result.stderr}")
            # Try -p1 as fallback
            with open(patch_path, "r") as f:
                result2 = subprocess.run(["patch", "-p1"], stdin=f, capture_output=True, text=True, cwd=self.sandbox_dir)
            if result2.returncode != 0:
                raise Exception(f"Failed to apply patch: {result.stderr}\nFallback failed: {result2.stderr}")
