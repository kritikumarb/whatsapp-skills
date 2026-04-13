from fastapi import FastAPI, Request, Response
import json
import base64

app = FastAPI()

# --- External Utilities (Provided by User) ---
def decrypt_payload(body_dict):
    """
    Decrypts Flow Endpoint requests.
    In a real-world scenario, you would use AES decryption with the shared secret.
    For this prototype, we'll return the decrypted payload directly.
    """
    # Simulate decryption
    return body_dict

def encrypt_payload(response_dict):
    """
    Encrypts Flow Endpoint responses.
    In a real-world scenario, you would use AES encryption.
    The response must be a Base64 string and Content-Type must be 'text/plain'.
    """
    # Simulate encryption and return Base64 string
    response_json = json.dumps(response_dict)
    return base64.b64encode(response_json.encode()).decode()

# --- Mock Data ---
DESTINATIONS = {
    "NYC": "New York",
    "LON": "London",
    "TKO": "Tokyo"
}

def get_seats(destination_id):
    """Mocks available seats for a given destination."""
    return [
        {"id": f"{destination_id}-1A", "title": f"1A (Window) - {destination_id}"},
        {"id": f"{destination_id}-2B", "title": f"2B (Aisle) - {destination_id}"},
        {"id": f"{destination_id}-3C", "title": f"3C (Exit Row) - {destination_id}"}
    ]

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    """
    data = json.loads(flow_response_json)
    print(f"Booking confirmed! Final Flow Data: {data}")
    return {"status": "success", "booking_data": data}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
    try:
        body = await request.json()
    except Exception:
        return Response(content="Invalid JSON", status_code=400)
        
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    data = decrypted_data.get("data", {})
    
    response_data = {"version": "3.1"}
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        # On selecting a destination, fetch available seats
        destination_id = data.get("destination")
        
        if destination_id in DESTINATIONS:
            response_data["screen"] = "SELECT_SEAT"
            response_data["data"] = {
                "destination_id": destination_id,
                "destination_name": DESTINATIONS[destination_id],
                "seats": get_seats(destination_id)
            }
        else:
            # Fallback or error state
            response_data["screen"] = "SELECT_DESTINATION"
            response_data["data"] = {
                "error": "Invalid destination selected"
            }
            
    encrypted_response = encrypt_payload(response_data)
    return Response(content=encrypted_response, media_type="text/plain")

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
