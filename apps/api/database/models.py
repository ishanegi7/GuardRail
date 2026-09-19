from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime
from datetime import datetime
from database.db import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    target_url = Column(String)
    openapi_spec = Column(JSON) # Store parsed representation or raw text

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    status = Column(String, default="running") # running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    vulnerability_type = Column(String)
    severity = Column(String)
    confidence = Column(String, default="HIGH")
    owasp_category = Column(String, default="API1:2023 - Broken Object Level Authorization")
    endpoint = Column(String)
    method = Column(String)
    description = Column(String)
    evidence = Column(JSON)
    patch_status = Column(String, default="pending") # pending, generated, applied, verified
    ai_explanation = Column(String, nullable=True)
    patch_diff = Column(String, nullable=True)
