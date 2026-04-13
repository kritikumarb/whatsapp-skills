from fastapi import FastAPI, Request, Response
from typing import Dict, Any

app = FastAPI()

# Placeholder encryption/decryption functions as per WhatsApp Flow guidelines
def decrypt_payload(body_dict: Dict[str, Any]) -> Dict[str, Any]:
    # In production, this would handle RSA/AES decryption
    return body_dict

def encrypt_payload(response_dict: Dict[str, Any]) -> str:
    # In production, this would handle AES encryption and Base64 encoding
    import json
    import base64
    return base64.b64encode(json.dumps(response_dict).encode()).decode()

SEATS_BY_DESTINATION = {
    "LHR": [{"id": "1A", "title": "1A (Window)"}, {"id": "1B", "title": "1B (Aisle)"}, {"id": "2C", "title": "2C (Middle)"}],
    "JFK": [{"id": "5A", "title": "5A (Window)"}, {"id": "5B", "title": "5B (Aisle)"}, {"id": "10C", "title": "10C (Window)"}],
    "DXB": [{"id": "12F", "title": "12F (Window)"}, {"id": "14D", "title": "14D (Aisle)"}],
    "SIN": [{"id": "20A", "title": "20A (Window)"}, {"id": "21B", "title": "21B (Aisle)"}, {"id": "22C", "title": "22C (Middle)"}]
}

@app.post("/whatsapp-flow")
async def handle_flow(request: Request):
    body = await request.json()
    payload = decrypt_payload(body)
    
    action = payload.get("action")
    version = payload.get("version", "3.1")
    
    if action == "ping":
        response = {
            "version": version,
            "data": {"status": "active"}
        }
    elif action == "data_exchange":
        screen = payload.get("screen")
        data = payload.get("data", {})
        
        if screen == "SELECT_DESTINATION":
            destination_id = data.get("destination")
            available_seats = SEATS_BY_DESTINATION.get(destination_id, [])
            
            response = {
                "version": version,
                "screen": "SELECT_SEAT",
                "data": {
                    "destination": destination_id,
                    "available_seats": available_seats
                }
            }
        else:
            response = {
                "version": version,
                "data": {"error": "Invalid screen"}
            }
    else:
        # Default fallback for submission or other actions
        response = {
            "version": version,
            "data": {"status": "success"}
        }

    encrypted_response = encrypt_payload(response)
    return Response(content=encrypted_response, media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
