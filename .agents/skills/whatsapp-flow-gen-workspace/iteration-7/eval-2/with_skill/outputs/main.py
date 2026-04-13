from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Simulated) ---
def decrypt_payload(body_dict):
    """Decrypts Flow Endpoint requests (Identity function for this task)."""
    return body_dict

def encrypt_payload(response_dict):
    """Encrypts Flow Endpoint responses (Identity function for this task)."""
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    """
    data = json.loads(flow_response_json)
    print(f"Final Flow Data Received: {data}")
    # Business logic here...
    return {"status": "success"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    screen = decrypted_data.get("screen")
    data = decrypted_data.get("data", {})
    
    response_data = {"version": "3.0"}
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "FETCH_CATEGORY_ITEMS":
            category_id = data.get("category_id")
            category_name = data.get("category_name")
            
            menu_items = {
                "starters": [
                    {"id": "s1", "title": "Bruschetta"},
                    {"id": "s2", "title": "Garlic Bread"},
                    {"id": "s3", "title": "Calamari"}
                ],
                "main": [
                    {"id": "m1", "title": "Grilled Salmon"},
                    {"id": "m2", "title": "Steak Frites"},
                    {"id": "m3", "title": "Chicken Alfredo"}
                ],
                "dessert": [
                    {"id": "d1", "title": "Tiramisu"},
                    {"id": "d2", "title": "Cheesecake"},
                    {"id": "d3", "title": "Brownie Sundae"}
                ]
            }
            
            response_data["screen"] = "ITEM_SCREEN"
            response_data["data"] = {
                "category_name": category_name,
                "items": menu_items.get(category_id, [])
            }
        else:
            # Fallback to category selection
            response_data["screen"] = "CATEGORY_SCREEN"
            response_data["data"] = {}
            
    content = encrypt_payload(response_data)
    return Response(content=content, media_type="text/plain")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Standard webhook to receive the final flow completion message."""
    body = await request.json()
    
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            for message in messages:
                if message.get("type") == "interactive":
                    interactive = message.get("interactive", {})
                    if interactive.get("type") == "nfm_reply":
                        response_json = interactive.get("nfm_reply", {}).get("response_json")
                        handle_submission(response_json)
    
    return {"status": "ok"}
