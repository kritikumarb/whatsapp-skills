from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Provided by User) ---
def decrypt_payload(body_dict):
    """
    In a real implementation, this would use private keys to decrypt the JWE.
    For this example, we return the body as-is or mock the decryption.
    """
    return body_dict

def encrypt_payload(response_dict):
    """
    In a real implementation, this would encrypt the response into a JWE.
    For this example, we return the JSON string.
    """
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    try:
        data = json.loads(flow_response_json)
        print(f"Final Flight Booking Received: {data}")
        # In a real app, you would save this to a database
        return {"status": "success", "booking_ref": "FLIGHT123"}
    except Exception as e:
        print(f"Error handling submission: {e}")
        return {"status": "error"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """
    Encrypted endpoint for ping and data_exchange.
    """
    try:
        body = await request.json()
        decrypted_data = decrypt_payload(body)
        
        action = decrypted_data.get("action")
        data = decrypted_data.get("data", {})
        
        response_data = {"version": "7.1"}
        
        if action == "ping":
            response_data["data"] = {"status": "active"}
            
        elif action == "data_exchange":
            trigger = data.get("data_exchange_trigger")
            
            if trigger == "fetch_seats":
                destination = data.get("destination", "NYC")
                
                # Mock seat availability based on destination
                if destination == "NYC":
                    seats = [
                        {"id": "1A", "title": "1A (Window) - $50"},
                        {"id": "2B", "title": "2B (Middle) - $0"},
                        {"id": "3C", "title": "3C (Aisle) - $20"}
                    ]
                elif destination == "LON":
                    seats = [
                        {"id": "10A", "title": "10A (Window) - $60"},
                        {"id": "11C", "title": "11C (Aisle) - $30"}
                    ]
                else:
                    seats = [
                        {"id": "5F", "title": "5F (Window) - $40"},
                        {"id": "6E", "title": "6E (Middle) - $0"}
                    ]
                
                response_data["screen"] = "SELECT_SEAT"
                response_data["data"] = {
                    "available_seats": seats
                }
            else:
                response_data["screen"] = "SELECT_DESTINATION"
                response_data["data"] = {"error": "Invalid trigger"}
        
        encrypted_response = encrypt_payload(response_data)
        return Response(content=encrypted_response, media_type="text/plain")
        
    except Exception as e:
        print(f"Flow Endpoint Error: {e}")
        return Response(content="Internal Server Error", status_code=500)

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """
    Standard webhook to receive the final flow completion message.
    """
    try:
        body = await request.json()
        
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    if message.get("type") == "interactive":
                        interactive = message.get("interactive", {})
                        if interactive.get("type") == "nfm_reply":
                            response_json = interactive.get("nfm_reply", {}).get("response_json")
                            handle_submission(response_json)
        
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook Error: {e}")
        return {"status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
