from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- Placeholder Utilities (Provided by User) ---
def decrypt_payload(body_dict):
    """
    Decrypts Flow Endpoint requests.
    In a production environment, you would use your private key to decrypt the payload.
    """
    return body_dict

def encrypt_payload(response_dict):
    """
    Encrypts Flow Endpoint responses.
    In a production environment, you would use the AES key and initial vector from the request
    to encrypt the response.
    """
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_data):
    """
    Processes the final flow completion data.
    """
    print(f"--- FLIGHT BOOKING CONFIRMED ---")
    print(f"Destination: {flow_data.get('destination')}")
    print(f"Seat: {flow_data.get('seat')}")
    print(f"--------------------------------")
    return {"status": "success"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    data = decrypted_data.get("data", {})
    
    # response_data structure for WhatsApp Flows Data API
    response_data = {
        "version": "3.0" # Data API version
    }
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "FETCH_SEATS":
            destination_id = data.get("destination")
            
            # Map ID to name for display
            dest_map = {
                "NYC": "New York",
                "LON": "London",
                "TYO": "Tokyo"
            }
            dest_name = dest_map.get(destination_id, "Unknown Destination")
            
            # Mock data for seats based on destination
            seats = [
                {"id": f"{destination_id}-1A", "title": "1A (Window)"},
                {"id": f"{destination_id}-1B", "title": "1B (Aisle)"},
                {"id": f"{destination_id}-2A", "title": "2A (Window)"},
                {"id": f"{destination_id}-2B", "title": "2B (Aisle)"},
                {"id": f"{destination_id}-3A", "title": "3A (Window)"},
                {"id": f"{destination_id}-3B", "title": "3B (Aisle)"}
            ]
            
            # Transition to SELECT_SEAT screen with the populated data
            response_data["screen"] = "SELECT_SEAT"
            response_data["data"] = {
                "destination_name": dest_name,
                "seats": seats
            }
        else:
             # Default response if trigger is unrecognized
             response_data["data"] = {"message": "Action completed."}
            
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
                        response_json_str = interactive.get("nfm_reply", {}).get("response_json")
                        if response_json_str:
                            flow_data = json.loads(response_json_str)
                            handle_submission(flow_data)
    
    return {"status": "ok"}
