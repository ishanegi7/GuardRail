import httpx
from typing import Dict, Any

async def run_bola_detector(engine, endpoint: Dict[str, Any]):
    path = endpoint["path"]
    method = endpoint["method"]
    
    # Simple heuristic: Path has a parameter like {id} or {invoice_id}
    if "{" not in path or method != "GET":
        return

    # Deterministic test for demo: We know /api/invoices returns invoices.
    # In a real engine, we'd do resource discovery. Here we hardcode the logic to simulate advanced discovery.
    
    if "invoices" in path and "{invoice_id}" in path:
        # Step 1: User A (Alice) gets her invoices
        alice_token = engine.tokens.get("alice@example.test")
        bob_token = engine.tokens.get("bob@example.test")
        
        if not alice_token or not bob_token:
            return

        async with httpx.AsyncClient() as client:
            headers_a = {"Authorization": f"Bearer {alice_token}"}
            res_a_list = await client.get(f"{engine.target_url}/api/invoices", headers=headers_a)
            
            if res_a_list.status_code != 200:
                return
            
            invoices = res_a_list.json()
            if not invoices:
                return
                
            # Pick Alice's first invoice
            target_invoice_id = invoices[0]["id"]
            
            # Step 2: User A accesses her own invoice (Baseline)
            res_a = await client.get(f"{engine.target_url}/api/invoices/{target_invoice_id}", headers=headers_a)
            
            # Step 3: User B attempts to access User A's invoice (Attack)
            headers_b = {"Authorization": f"Bearer {bob_token}"}
            res_b = await client.get(f"{engine.target_url}/api/invoices/{target_invoice_id}", headers=headers_b)
            
            if res_b.status_code == 200 and res_b.json() == res_a.json():
                # BOLA detected!
                evidence = {
                    "baseline_request": {
                        "method": method,
                        "url": f"/api/invoices/{target_invoice_id}",
                        "headers": {"Authorization": "Bearer TOKEN_A (Alice)"}
                    },
                    "baseline_response": {
                        "status_code": res_a.status_code,
                        "body": res_a.json()
                    },
                    "attack_request": {
                         "method": method,
                        "url": f"/api/invoices/{target_invoice_id}",
                        "headers": {"Authorization": "Bearer TOKEN_B (Bob)"}
                    },
                    "attack_response": {
                        "status_code": res_b.status_code,
                        "body": res_b.json()
                    }
                }
                
                engine.report_finding({
                    "vulnerability_type": "BOLA / IDOR",
                    "severity": "HIGH",
                    "confidence": "HIGH",
                    "owasp_category": "API1:2023 - Broken Object Level Authorization",
                    "endpoint": path,
                    "method": method,
                    "description": f"User B successfully accessed an invoice owned by User A. Both Alice and Bob received identical 200 OK responses with private invoice data.",
                    "evidence": evidence
                })
