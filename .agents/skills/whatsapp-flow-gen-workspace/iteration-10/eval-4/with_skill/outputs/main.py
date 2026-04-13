from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Provided by User) ---
def decrypt_payload(body_dict):
    """Decrypts Flow Endpoint requests."""
    return body_dict

def encrypt_payload(response_dict):
    """Encrypts Flow Endpoint responses."""
    # In a real implementation, this would return an encrypted string.
    # For this task, we return the JSON string as per common testing patterns.
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    data = json.loads(flow_response_json)
    print(f"Final Flow Data Received: {data}")
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
        
        if trigger == "check_availability":
            selected_date = data.get("selected_date")
            # Mock availability logic: available if it's not a weekend (simplified)
            # In a real app, this would query a database.
            is_available = True
            if selected_date and ("-06" in selected_date or "-07" in selected_date): # Simplified mock
                is_available = False
            
            response_data["screen"] = "RESULT"
            response_data["data"] = {
                "is_available": is_available,
                "message": f"Checking availability for {selected_date}..." if selected_date else "No date selected."
            }
            if is_available:
                response_data["data"]["message"] = f"Date {selected_date} is available!"
            else:
                response_data["data"]["message"] = f"Date {selected_date} is already booked."
        else:
             response_data["screen"] = "WELCOME"
             response_data["data"] = {"message": "Invalid trigger."}
            
    encrypted_response = encrypt_payload(response_data)
    return Response(content=encrypted_response, media_type="text/plain")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
