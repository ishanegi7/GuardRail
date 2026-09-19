from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from scanner import run_scan
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GuardRail AI Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthTokens(BaseModel):
    user_a: str
    user_b: str

class ScanRequest(BaseModel):
    schema_type: str
    schema_content: str
    target_base_url: str
    auth_tokens: AuthTokens

class EvidenceRequest(BaseModel):
    method: str
    url: str
    actor: str

class EvidenceResponse(BaseModel):
    status: int
    leaked_fields: List[str]

class Evidence(BaseModel):
    request: EvidenceRequest
    response: EvidenceResponse

class Remediation(BaseModel):
    explanation: str
    patch_diff: str

class Finding(BaseModel):
    id: str
    type: str
    severity: str
    endpoint: str
    evidence: Evidence
    remediation: Remediation

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    findings_count: int
    findings: List[Finding]

@app.post("/api/v1/scans", response_model=ScanResponse)
async def create_scan(request: ScanRequest):
    result = await run_scan(request)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
