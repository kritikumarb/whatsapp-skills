from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Security Layer) ---
def decrypt_payload(body_dict):
    """
    Decrypts Flow Endpoint requests.
    In a real implementation, this would use the WhatsApp business private key.
    """
    return body_dict

def encrypt_payload(response_dict):
    """
    Encrypts Flow Endpoint responses.
    In a real implementation, this would use the symmetric key from the request.
    """
    # Return as JSON string for demonstration, though WhatsApp expects encrypted base64
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    data = json.loads(flow_response_json)
    print(f"Booking Confirmed: {data}")
    # Example: Save to DB or send confirmation email
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
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "fetch_seats":
            dest_id = data.get("destination_id")
            
            # Mock data based on destination
            dest_map = {
                "LHR": "London (LHR)",
                "CDG": "Paris (CDG)",
                "JFK": "New York (JFK)"
            }
            dest_name = dest_map.get(dest_id, "Unknown Destination")
            
            # Simulated available seats
            available_seats = [
                {"id": f"{dest_id}-1A", "title": "1A (Window)"},
                {"id": f"{dest_id}-1B", "title": "1B (Middle)"},
                {"id": f"{dest_id}-1C", "title": "1C (Aisle)"},
                {"id": f"{dest_id}-2A", "title": "2A (Window)"}
            ]
            
            response_data["screen"] = "SEAT_SCREEN"
            response_data["data"] = {
                "destination_id": dest_id,
                "destination_name": dest_name,
                "seats": available_seats
            }
        else:
            response_data["screen"] = "DESTINATION_SCREEN"
            response_data["data"] = {"error": "Invalid trigger"}
            
    encrypted_response = encrypt_payload(response_data)
    # Note: WhatsApp expects text/plain for the encrypted body
    return Response(content=encrypted_response, media_type="text/plain")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Standard webhook to receive the final flow completion message."""
    body = await request.json()
    
    # Check for messages -> interactive -> nfm_reply (Flow response)
    if "entry" in body:
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    for message in value.get("messages", []):
                        if message.get("type") == "interactive":
                            interactive = message.get("interactive", {})
                            if interactive.get("type") == "nfm_reply":
                                response_json = interactive.get("nfm_reply", {}).get("response_json")
                                handle_submission(response_json)
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
