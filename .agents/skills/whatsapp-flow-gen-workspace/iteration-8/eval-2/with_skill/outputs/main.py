from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Simulated) ---
def decrypt_payload(body_dict):
    """Decrypts Flow Endpoint requests (Simulated for this task)."""
    return body_dict

def encrypt_payload(response_dict):
    """Encrypts Flow Endpoint responses (Simulated for this task)."""
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    data = json.loads(flow_response_json)
    category = data.get("category")
    item_id = data.get("item_id")
    
    print(f"Order Received!")
    print(f"Category: {category}")
    print(f"Item ID: {item_id}")
    
    # In a real app, save to database or trigger order processing
    return {"status": "success", "order_id": "12345"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    data = decrypted_data.get("data", {})
    
    # Note: data_api_version must be "3.0"
    response_data = {"version": "3.0"}
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        # MANDATORY: Check for the trigger name
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "category_selected":
            category_id = data.get("category")
            items = []
            category_name = ""
            
            if category_id == "starters":
                category_name = "Starters"
                items = [
                    {"id": "bruschetta", "title": "Bruschetta"},
                    {"id": "soup", "title": "Soup of the Day"},
                    {"id": "salad", "title": "Caesar Salad"}
                ]
            elif category_id == "main":
                category_name = "Main Course"
                items = [
                    {"id": "pizza", "title": "Margherita Pizza"},
                    {"id": "pasta", "title": "Spaghetti Carbonara"},
                    {"id": "burger", "title": "Classic Cheeseburger"}
                ]
            elif category_id == "dessert":
                category_name = "Dessert"
                items = [
                    {"id": "cake", "title": "Chocolate Lava Cake"},
                    {"id": "ice_cream", "title": "Vanilla Ice Cream"},
                    {"id": "fruit", "title": "Fresh Fruit Platter"}
                ]
            
            response_data["screen"] = "ITEM_SELECTION"
            response_data["data"] = {
                "items": items,
                "category_name": category_name
            }
        else:
            # Default fallback
            response_data["screen"] = "CATEGORY_SELECTION"
            response_data["data"] = {}
            
    encrypted_response = encrypt_payload(response_data)
    return Response(content=encrypted_response, media_type="application/json")

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
