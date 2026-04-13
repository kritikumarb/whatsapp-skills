from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Simulated) ---
def decrypt_payload(body_dict):
    """Simulates decryption of Flow Endpoint requests."""
    return body_dict

def encrypt_payload(response_dict):
    """Simulates encryption of Flow Endpoint responses."""
    # In a real scenario, this would return an encrypted string
    return json.dumps(response_dict)

# --- Business Logic ---
def get_available_seats(destination):
    """Returns available seats for a given destination."""
    # Simulation: Different seats based on destination
    if destination == "NYC":
        return [
            {"id": "1A", "title": "1A (Window)"},
            {"id": "1B", "title": "1B (Middle)"},
            {"id": "1C", "title": "1C (Aisle)"}
        ]
    elif destination == "LON":
        return [
            {"id": "2A", "title": "2A (Window)"},
            {"id": "2B", "title": "2B (Middle)"},
            {"id": "2C", "title": "2C (Aisle)"}
        ]
    elif destination == "PAR":
        return [
            {"id": "3A", "title": "3A (Window)"},
            {"id": "3B", "title": "3B (Middle)"},
            {"id": "3C", "title": "3C (Aisle)"}
        ]
    else:
        return [
            {"id": "4A", "title": "4A (Window)"},
            {"id": "4B", "title": "4B (Middle)"},
            {"id": "4C", "title": "4C (Aisle)"}
        ]

def handle_submission(flow_response_json):
    """Processes the final flight booking data."""
    data = json.loads(flow_response_json)
    print(f"Booking Confirmed: {data}")
    return {"status": "success"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Endpoint for WhatsApp Flow interactions."""
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    screen = decrypted_data.get("screen")
    data = decrypted_data.get("data", {})
    
    response_data = {"version": "3.1"}
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        # Check current screen to determine next action
        if screen == "SELECT_DESTINATION":
            destination = data.get("destination")
            available_seats = get_available_seats(destination)
            
            response_data["screen"] = "SELECT_SEAT"
            response_data["data"] = {
                "destination": destination,
                "seats": available_seats
            }
        else:
            response_data["screen"] = "SELECT_DESTINATION"
            response_data["data"] = {"message": "Invalid request sequence."}
            
    encrypted_response = encrypt_payload(response_data)
    return Response(content=encrypted_response, media_type="application/json")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Webhook to receive final flow completion message."""
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
