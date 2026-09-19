import httpx
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from database import models
from scanner.detectors.bola import run_bola_detector
from scanner.detectors.broken_auth import run_auth_detector
from scanner.detectors.mass_assignment import run_mass_assignment_detector

class ScannerEngine:
    def __init__(self, target_url: str, openapi_spec: dict, scan_id: int, db: Session):
        self.target_url = target_url
        self.spec = openapi_spec
        self.scan_id = scan_id
        self.db = db
        self.tokens = {}

    async def init_identities(self):
        # Deterministic logic for the hackathon demo. In real life, users would configure this.
        async with httpx.AsyncClient() as client:
            for email, pwd in [("alice@example.test", "password"), ("bob@example.test", "password"), ("admin@example.test", "admin")]:
                try:
                    res = await client.post(f"{self.target_url}/api/auth/login", data={"username": email, "password": pwd})
                    if res.status_code == 200:
                        self.tokens[email] = res.json()["access_token"]
                except Exception as e:
                    print(f"Failed to login {email}: {e}")

    async def run(self):
        # Reset the demo API database
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{self.target_url}/api/reset")
                print("Demo API reset successful.")
        except Exception as e:
            print(f"Warning: Could not reset demo API: {e}")

        await self.init_identities()
        if not self.tokens:
            print("Failed to initialize test identities. Aborting scan.")
            return

        endpoints = self.extract_endpoints(self.spec)
        
        # We run the detectors sequentially for simplicity in this MVP, 
        # but in a real app we'd use asyncio.gather for concurrent execution.
        for ep in endpoints:
            await run_auth_detector(self, ep)
            await run_bola_detector(self, ep)
            await run_mass_assignment_detector(self, ep)
            
        # Update scan status
        scan = self.db.query(models.Scan).filter(models.Scan.id == self.scan_id).first()
        if scan:
            scan.status = "completed"
            scan.completed_at = datetime.utcnow()
            self.db.commit()

    def extract_endpoints(self, spec: dict):
        endpoints = []
        paths = spec.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                    continue
                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "details": details
                })
        return endpoints

    def report_finding(self, finding_data: dict):
        finding = models.Finding(
            scan_id=self.scan_id,
            vulnerability_type=finding_data["vulnerability_type"],
            severity=finding_data["severity"],
            confidence=finding_data.get("confidence", "HIGH"),
            owasp_category=finding_data.get("owasp_category", ""),
            endpoint=finding_data["endpoint"],
            method=finding_data["method"],
            description=finding_data["description"],
            evidence=finding_data["evidence"]
        )
        self.db.add(finding)
        self.db.commit()

async def run_scan(scan_id: int, project: models.Project, db: Session):
    # This function is run as a background task. 
    # Because FastAPI's Depends(get_db) session doesn't work well across threads in background tasks sometimes if we don't manage it carefully.
    # But since we passed db from main, we use it (or we should create a new one). 
    # To be safe, we create a new session.
    from database.db import SessionLocal
    local_db = SessionLocal()
    try:
        engine = ScannerEngine(project.target_url, project.openapi_spec, scan_id, local_db)
        # Create a new event loop or use existing since we are in async context?
        # background_tasks runs in threadpool. So we need asyncio.run if this is synchronous wrapper.
        # Wait, run_scan is def or async def? I defined it as async def... wait, I didn't. 
        # Let's fix that. It needs to be a sync wrapper if we use background_tasks.add_task(sync_func) or async if we use async func.
        # BackgroundTasks handles both.
        await engine.run()
    finally:
        local_db.close()
