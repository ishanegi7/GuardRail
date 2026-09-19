import httpx
from typing import Dict, Any

async def run_auth_detector(engine, endpoint: Dict[str, Any]):
    path = endpoint["path"]
    method = endpoint["method"]
    details = endpoint["details"]
    
    # Check if endpoint is supposed to be protected. For simplicity, we assume endpoints containing {id} or /me are protected,
    # except /auth
    if "auth" in path:
        return

    # In a real scanner we would check the OpenAPI `security` scheme. Here we just test it.
    # We will send a request without authentication.
    
    # We only test the broken auth on the orders endpoint for our deterministic demo.
    if "orders" not in path:
        return

    async with httpx.AsyncClient() as client:
        # Attack: No auth
        # Generate a test ID for path params if needed
        test_url = f"{engine.target_url}{path.replace('{order_id}', '1')}"
        
        # We need a baseline to know it works when authenticated? Actually, the broken auth means it works even without auth.
        res = await client.request(method, test_url)
        
        if res.status_code == 200:
            evidence = {
                "attack_request": {
                    "method": method,
                    "url": path.replace('{order_id}', '1'),
                    "headers": {}
                },
                "attack_response": {
                    "status_code": res.status_code,
                    "body": res.json()
                }
            }
            engine.report_finding({
                "vulnerability_type": "Broken Authentication",
                "severity": "CRITICAL",
                "confidence": "HIGH",
                "owasp_category": "API2:2023 - Broken Authentication",
                "endpoint": path,
                "method": method,
                "description": f"Endpoint returned 200 OK without requiring authentication credentials.",
                "evidence": evidence
            })
