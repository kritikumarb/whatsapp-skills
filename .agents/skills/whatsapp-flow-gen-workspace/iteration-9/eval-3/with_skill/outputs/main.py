from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Placeholders) ---
def decrypt_payload(body_dict):
    """
    Decrypts Flow Endpoint requests.
    In a real implementation, use the private key to decrypt.
    """
    return body_dict

def encrypt_payload(response_dict):
    """
    Encrypts Flow Endpoint responses.
    In a real implementation, use the session key to encrypt.
    """
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_data):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    print(f"Booking Confirmed: {flow_data}")
    # Logic to save the booking to a database would go here.
    return {"status": "success"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    data = decrypted_data.get("data", {})
    
    # Standard response structure
    response_data = {
        "version": "3.1" # Data API version
    }
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "fetch_available_times":
            # Logic to fetch available times based on service and date
            service = data.get("service")
            selected_date = data.get("selected_date")
            
            # Simulated data
            available_times = [
                {"id": "09:00", "title": "09:00 AM"},
                {"id": "10:30", "title": "10:30 AM"},
                {"id": "14:00", "title": "02:00 PM"},
                {"id": "16:30", "title": "04:30 PM"}
            ]
            
            # The prompt requires: "A 'Notice' text should be visible only if 'data.show_notice' is false."
            # So if we want to SHOW the notice, we set show_notice to false.
            # If we want to HIDE the notice, we set show_notice to true.
            show_notice = False 
            
            response_data["screen"] = "TIME_SELECTION"
            response_data["data"] = {
                "times": available_times,
                "show_notice": show_notice,
                "service": service,
                "selected_date": selected_date
            }
        else:
            response_data["screen"] = "SERVICE_SELECTION"
            response_data["data"] = {}
            
    encrypted_response = encrypt_payload(response_data)
    # Note: Content-type should be text/plain for encrypted flows, 
    # but using application/json here as these are placeholders.
    return Response(content=encrypted_response, media_type="application/json")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Standard webhook to receive the final flow completion message."""
    body = await request.json()
    
    # Traverse the WhatsApp Business Platform webhook structure
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                if message.get("type") == "interactive":
                    interactive = message.get("interactive", {})
                    if interactive.get("type") == "nfm_reply":
                        # The final flow response is a JSON string
                        response_json = interactive.get("nfm_reply", {}).get("response_json")
                        flow_data = json.loads(response_json)
                        handle_submission(flow_data)
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
