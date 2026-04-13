from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Simulated) ---
# In a real scenario, these would handle WhatsApp Flow encryption/decryption
def decrypt_payload(body_dict):
    """Simulates decryption of Flow Endpoint requests."""
    return body_dict

def encrypt_payload(response_dict):
    """Simulates encryption of Flow Endpoint responses."""
    # Returning plain JSON for this exercise, but usually this is an encrypted string
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    data = json.loads(flow_response_json)
    print(f"Booking Confirmed: {data}")
    # Logic to save booking to database would go here
    return {"status": "success", "booking_details": data}

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
        # Check for the mandatory data_exchange_trigger
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "GET_AVAILABLE_SEATS":
            destination = data.get("destination", "unknown")
            
            # Simulate fetching seats from a database based on destination
            # Returning a dynamic list of seats
            mock_seats = [
                {"id": f"seat_{destination}_1A", "title": "1A (Window)"},
                {"id": f"seat_{destination}_2B", "title": "2B (Aisle)"},
                {"id": f"seat_{destination}_3C", "title": "3C (Window)"},
                {"id": f"seat_{destination}_4D", "title": "4D (Aisle)"}
            ]
            
            # Transition to the next screen with the fetched data
            response_data["screen"] = "SELECT_SEAT"
            response_data["data"] = {
                "destination_name": destination.replace("_", " ").title(),
                "available_seats": mock_seats
            }
        else:
            # Default fallback
            response_data["data"] = {"error": "Invalid trigger"}
            
    encrypted_response = encrypt_payload(response_data)
    # Media type is usually text/plain for encrypted flows, but application/json for simulation
    return Response(content=encrypted_response, media_type="application/json")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Standard webhook to receive the final flow completion message."""
    body = await request.json()
    
    # Check for messages -> interactive -> nfm_reply (Flow response)
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
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
