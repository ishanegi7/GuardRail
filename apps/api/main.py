from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Security, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.db import engine, Base, SessionLocal, get_db
from database import models, schemas
import os
import httpx
from scanner.engine import run_scan
from ai.patcher import generate_patch_for_finding, apply_and_verify_patch

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    expected_key = os.environ.get("GUARDRAIL_API_KEY")
    if expected_key and api_key != expected_key:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

app = FastAPI(title="GuardRail AI API", dependencies=[Depends(verify_api_key)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Seed a demo project if it doesn't exist
    db = SessionLocal()
    if db.query(models.Project).count() == 0:
        demo_url = os.environ.get("DEMO_API_URL", "http://demo-api:8080")
        try:
            # Try to fetch openapi spec from demo-api
            resp = httpx.get(f"{demo_url}/openapi.json")
            if resp.status_code == 200:
                proj = models.Project(name="Demo Target", target_url=demo_url, openapi_spec=resp.json())
                db.add(proj)
                db.commit()
        except Exception as e:
            print("Could not fetch openapi from demo-api", e)
    db.close()

@app.get("/api/projects", response_model=list[schemas.Project])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.post("/api/scans", response_model=schemas.Scan)
def create_scan(scan: schemas.ScanCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == scan.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_scan = models.Scan(project_id=scan.project_id)
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    background_tasks.add_task(run_scan, db_scan.id, project.id)
    
    return db_scan

@app.get("/api/scans", response_model=list[schemas.Scan])
def get_scans(db: Session = Depends(get_db)):
    return db.query(models.Scan).order_by(models.Scan.id.desc()).all()

@app.get("/api/findings", response_model=list[schemas.Finding])
def get_findings(scan_id: int = None, db: Session = Depends(get_db)):
    q = db.query(models.Finding)
    if scan_id:
        q = q.filter(models.Finding.scan_id == scan_id)
    return q.all()

@app.get("/api/findings/{finding_id}", response_model=schemas.Finding)
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    finding = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not finding:
         raise HTTPException(status_code=404, detail="Finding not found")
    return finding

@app.post("/api/findings/{finding_id}/generate-patch", response_model=schemas.Finding)
async def api_generate_patch(finding_id: int, db: Session = Depends(get_db)):
    finding = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not finding:
         raise HTTPException(status_code=404, detail="Finding not found")
    
    if finding.patch_status == "pending":
        await generate_patch_for_finding(finding, db)
    return finding

@app.post("/api/findings/{finding_id}/verify-patch", response_model=schemas.Finding)
async def api_verify_patch(finding_id: int, db: Session = Depends(get_db)):
    finding = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not finding:
         raise HTTPException(status_code=404, detail="Finding not found")
    
    success = await apply_and_verify_patch(finding, db)
    return finding
