import httpx
from typing import Dict, Any

async def run_mass_assignment_detector(engine, endpoint: Dict[str, Any]):
    path = endpoint["path"]
    method = endpoint["method"]
    
    # Target the PATCH /api/users/{user_id}
    if "users" not in path or method != "PATCH":
        return

    alice_token = engine.tokens.get("alice@example.test")
    if not alice_token:
        return

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {alice_token}"}
        
        # Get Alice's ID (which is 1)
        res_me = await client.get(f"{engine.target_url}/api/users/me", headers=headers)
        if res_me.status_code != 200:
            return
            
        alice_id = res_me.json()["id"]
        
        # Attack: Try to elevate privileges by mass assignment
        attack_payload = {
            "full_name": "Alice Hacker",
            "is_admin": True,
            "role": "admin"
        }
        
        res_patch = await client.patch(f"{engine.target_url}/api/users/{alice_id}", headers=headers, json=attack_payload)
        
        if res_patch.status_code == 200:
            patched_user = res_patch.json()
            if patched_user.get("is_admin") is True or patched_user.get("role") == "admin":
                # Revert to keep the demo environment stable
                await client.patch(f"{engine.target_url}/api/users/{alice_id}", headers=headers, json={"is_admin": False, "role": "user"})
                
                evidence = {
                    "attack_request": {
                        "method": method,
                        "url": f"/api/users/{alice_id}",
                        "headers": {"Authorization": "Bearer TOKEN_A (Alice)"},
                        "body": attack_payload
                    },
                    "attack_response": {
                        "status_code": res_patch.status_code,
                        "body": res_patch.json()
                    }
                }
                
                engine.report_finding({
                    "vulnerability_type": "Mass Assignment",
                    "severity": "HIGH",
                    "confidence": "HIGH",
                    "owasp_category": "API3:2023 - Broken Object Property Level Authorization",
                    "endpoint": path,
                    "method": method,
                    "description": "User successfully escalated privileges by injecting 'is_admin' and 'role' fields in the update request.",
                    "evidence": evidence
                })
