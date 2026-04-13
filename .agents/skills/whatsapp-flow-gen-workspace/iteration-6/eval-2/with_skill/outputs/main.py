from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- Menu Data ---
MENU_DATA = {
    "starters": [
        {"id": "bruschetta", "title": "Bruschetta"},
        {"id": "garlic_bread", "title": "Garlic Bread"},
        {"id": "tomato_soup", "title": "Tomato Soup"}
    ],
    "main": [
        {"id": "margherita_pizza", "title": "Margherita Pizza"},
        {"id": "penne_pasta", "title": "Penne Pasta"},
        {"id": "veggie_burger", "title": "Veggie Burger"}
    ],
    "dessert": [
        {"id": "chocolate_cake", "title": "Chocolate Cake"},
        {"id": "vanilla_ice_cream", "title": "Vanilla Ice Cream"},
        {"id": "tiramisu", "title": "Tiramisu"}
    ]
}

# --- External Utilities (Mocks for Flow Encryption) ---
def decrypt_payload(body_dict):
    """Decrypts Flow Endpoint requests. In a real app, use WhatsApp's crypto."""
    return body_dict

def encrypt_payload(response_dict):
    """Encrypts Flow Endpoint responses. In a real app, use WhatsApp's crypto."""
    # Returning as JSON string for the mock/test environment
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    data = json.loads(flow_response_json)
    print(f"Final Flow Data Received: {data}")
    # Here you would typically save to database or send an order confirmation
    return {"status": "success"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    data = decrypted_data.get("data", {})
    
    response_data = {"version": "3.1"}
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        # MANDATORY: Check for the trigger name
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "FETCH_ITEMS":
             category_id = data.get("category_id")
             category_name = data.get("category_name", "Menu")
             items = MENU_DATA.get(category_id, [])
             
             response_data["screen"] = "SCREEN_TWO"
             response_data["data"] = {
                 "category_name": category_name,
                 "items": items
             }
        else:
             response_data["screen"] = "SCREEN_ONE"
             response_data["data"] = {"error": "Invalid trigger"}
            
    encrypted_response = encrypt_payload(response_data)
    return Response(content=encrypted_response, media_type="text/plain")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Standard webhook to receive the final flow completion message."""
    body = await request.json()
    
    # Check for messages -> interactive -> nfm_reply (Flow response)
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                if message.get("type") == "interactive":
                    interactive = message.get("interactive", {})
                    if interactive.get("type") == "nfm_reply":
                        # The final flow JSON is here
                        response_json = interactive.get("nfm_reply", {}).get("response_json")
                        handle_submission(response_json)
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
