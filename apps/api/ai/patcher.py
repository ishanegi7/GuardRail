import os
import httpx
try:
    from litellm import completion
except ImportError:
    completion = None

from sqlalchemy.orm import Session
from database import models
from target_manager import TargetManager

SANDBOX_DIR = os.environ.get("SANDBOX_DIR", "/sandbox/demo-api")

# Fallback deterministic BOLA patch
DETERMINISTIC_BOLA_PATCH = """--- routers/invoices.py
+++ routers/invoices.py
@@ -16,6 +16,8 @@
 def read_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
     invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
     if invoice is None:
         raise HTTPException(status_code=404, detail="Invoice not found")
+    if invoice.owner_id != current_user.id:
+        raise HTTPException(status_code=403, detail="Forbidden")
     return invoice
"""

async def generate_patch_for_finding(finding: models.Finding, db: Session):
    llm_provider = os.environ.get("LLM_PROVIDER", "gemini")
    api_key = os.environ.get(f"{llm_provider.upper()}_API_KEY", "")
    
    source_file = None
    if "invoices" in finding.endpoint:
        source_file = "routers/invoices.py"
    elif "users" in finding.endpoint:
        source_file = "routers/users.py"
    elif "orders" in finding.endpoint:
        source_file = "routers/orders.py"
        
    if not source_file:
        return None
        
    full_path = os.path.join(SANDBOX_DIR, source_file)
    try:
        with open(full_path, "r") as f:
            source_code = f.read()
    except Exception as e:
        print(f"Could not read source code: {e}")
        return None

    # Deterministic fallback if no LLM key or LLM fails
    def use_fallback():
        finding.ai_explanation = "AI unavailable — generated using GuardRail's deterministic remediation fallback. The vulnerability is caused by missing object-level authorization checks. We need to verify the requested object belongs to the currently authenticated user."
        finding.patch_diff = DETERMINISTIC_BOLA_PATCH
        finding.patch_status = "generated"
        db.commit()
        return finding

    if not api_key or completion is None:
        if completion is None:
            print("LiteLLM is not installed. Using deterministic fallback.")
        else:
            print("No LLM API key provided. Using deterministic fallback.")
        return use_fallback()

    model = "gpt-4o"
    if llm_provider == "gemini":
        model = "gemini/gemini-1.5-pro"
    elif llm_provider == "anthropic":
        model = "claude-3-5-sonnet-20240620"
        
    prompt = f"""
    You are an expert Application Security Engineer. We found a {finding.vulnerability_type} vulnerability.
    
    Endpoint: {finding.method} {finding.endpoint}
    Description: {finding.description}
    Evidence:
    {finding.evidence}
    
    Here is the source code for the router ({source_file}):
    ```python
    {source_code}
    ```
    
    Task 1: Explain the root cause of this vulnerability in 2-3 sentences.
    Task 2: Provide a unified diff patch to fix this vulnerability. Output ONLY the unified diff block wrapped in ```diff ... ```. Do not provide any other code blocks.
    The diff should be applicable directly to the file. Ensure the fix properly implements authorization (e.g. comparing owner_id to current_user.id for BOLA, or checking if the user is_admin for Mass Assignment).
    """

    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        output = response.choices[0].message.content
        
        explanation = ""
        diff = ""
        
        if "```diff" in output:
            parts = output.split("```diff")
            explanation = parts[0].strip()
            diff = parts[1].split("```")[0].strip()
        else:
            explanation = output
            
        finding.ai_explanation = explanation
        finding.patch_diff = diff
        finding.patch_status = "generated"
        db.commit()
        return finding
    except Exception as e:
        print(f"LLM Error: {e}")
        return use_fallback()

async def apply_and_verify_patch(finding: models.Finding, db: Session):
    if not finding.patch_diff:
        return False
        
    source_file = None
    if "invoices" in finding.endpoint:
        source_file = "routers/invoices.py"
    elif "users" in finding.endpoint:
        source_file = "routers/users.py"
    elif "orders" in finding.endpoint:
        source_file = "routers/orders.py"
        
    if not source_file:
        return False

    tm = TargetManager()
    
    try:
        print("Creating isolated workspace...")
        finding.patch_status = "patch_applying"
        db.commit()
        
        tm.create_isolated_workspace()
        
        print("Applying patch...")
        tm.apply_patch(finding.patch_diff, source_file)
        
        finding.patch_status = "applied"
        db.commit()
        
        print("Starting isolated target...")
        finding.patch_status = "verifying"
        db.commit()
        
        tm.start_target()
        
        # Verify the exact exploit
        from scanner.engine import ScannerEngine
        # We need a new scanner engine instance against the isolated target URL
        isolated_url = tm.get_target_url()
        # Create a mock project for the engine
        from database.models import Project
        mock_proj = Project(target_url=isolated_url, openapi_spec={})
        
        verifier = ScannerEngine(isolated_url, {}, finding.scan_id, db)
        await verifier.init_identities()
        
        # Run BOLA exploit verification
        # The original exploit is in finding.evidence
        evidence = finding.evidence
        attack_req = evidence.get("attack_request")
        
        if attack_req:
            print("Re-running attack request...")
            async with httpx.AsyncClient() as client:
                # The auth token inside the evidence is labeled "Bearer TOKEN_B (Bob)".
                # We need the real Bob token from verifier.
                bob_token = verifier.tokens.get("bob@example.test")
                headers = {"Authorization": f"Bearer {bob_token}"}
                
                res = await client.request(
                    attack_req["method"],
                    f"{isolated_url}{attack_req['url']}",
                    headers=headers
                )
                
                print(f"Verification response: {res.status_code}")
                if res.status_code in [401, 403, 404]:
                    # Exploit blocked!
                    finding.patch_status = "verified"
                else:
                    finding.patch_status = "verification_failed"
        else:
            finding.patch_status = "verification_failed"
            
        db.commit()
    except Exception as e:
        print(f"Error applying/verifying patch: {e}")
        finding.patch_status = "error"
        db.commit()
    finally:
        tm.stop_target()

    return finding.patch_status == "verified"
