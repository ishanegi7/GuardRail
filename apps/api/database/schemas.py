from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    target_url: str
    openapi_spec: dict

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True

class ScanBase(BaseModel):
    project_id: int

class ScanCreate(ScanBase):
    pass

class Scan(ScanBase):
    id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FindingBase(BaseModel):
    scan_id: int
    vulnerability_type: str
    severity: str
    confidence: str = "HIGH"
    owasp_category: str = "API1:2023 - Broken Object Level Authorization"
    endpoint: str
    method: str
    description: str
    evidence: dict
    patch_status: str = "pending"

class FindingCreate(FindingBase):
    pass

class Finding(FindingBase):
    id: int
    ai_explanation: Optional[str] = None
    patch_diff: Optional[str] = None

    class Config:
        from_attributes = True

class PatchRequest(BaseModel):
    finding_id: int
