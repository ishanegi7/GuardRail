import pytest
from database import models
from ai.patcher import DETERMINISTIC_BOLA_PATCH, DETERMINISTIC_BROKEN_AUTH_PATCH

def test_bola_fallback_patch_content():
    assert "invoice.owner_id != current_user.id" in DETERMINISTIC_BOLA_PATCH

def test_broken_auth_fallback_patch_content():
    assert "current_user.is_admin" in DETERMINISTIC_BROKEN_AUTH_PATCH

def test_finding_model_creation():
    finding = models.Finding(
        scan_id=1,
        vulnerability_type="BOLA",
        severity="CRITICAL",
        endpoint="/api/invoices/1",
        method="GET",
        description="BOLA detected",
        evidence={}
    )
    assert finding.vulnerability_type == "BOLA"
    assert finding.severity == "CRITICAL"
