from fastapi import FastAPI, Request, Response
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Mock Encryption/Decryption (Placeholders for real implementation) ---
def decrypt_payload(body_dict: dict) -> dict:
    """
    In a real implementation, you would use your private key to decrypt the payload.
    For this prototype, we assume the payload is already decrypted or handled by a proxy.
    """
    return body_dict

def encrypt_payload(response_dict: dict) -> str:
    """
    In a real implementation, you would use the public key provided by WhatsApp to encrypt the response.
    For this prototype, we return the JSON string directly (or a mock encrypted string).
    """
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_data: dict):
    """
    Processes the final flow completion data received via the webhook.
    """
    logger.info(f"Final Appointment Booking Received: {flow_data}")
    # Here you would typically save to a database or trigger a confirmation email/SMS.
    return {"status": "success", "message": "Appointment recorded"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """
    Encrypted endpoint for ping and data_exchange during the Flow execution.
    """
    try:
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
            
            if trigger == "fetch_available_times":
                selected_date = data.get("selected_date")
                service = data.get("service")
                
                # Mock logic to fetch available times
                # In a real app, you would query your scheduling database
                time_slots = [
                    {"id": "09:00", "title": "09:00 AM"},
                    {"id": "10:00", "title": "10:00 AM"},
                    {"id": "11:00", "title": "11:00 AM"},
                    {"id": "14:00", "title": "02:00 PM"},
                    {"id": "15:00", "title": "03:00 PM"}
                ]
                
                response_data["screen"] = "TIME_SELECTION"
                response_data["data"] = {
                    "time_slots": time_slots,
                    "selected_date": selected_date,
                    "service": service
                }
            else:
                # Handle unknown triggers
                response_data["data"] = {"error": "Unknown data exchange trigger"}
        
        else:
            response_data["data"] = {"error": f"Unsupported action: {action}"}
            
        encrypted_response = encrypt_payload(response_data)
        return Response(content=encrypted_response, media_type="text/plain")

    except Exception as e:
        import traceback
        from fastapi.responses import PlainTextResponse
        traceback.print_exc()
        # Use the screen ID from decrypted_data if available
        response = {
            "screen": decrypted_data.get('screen', '') if 'decrypted_data' in locals() else '',
            "data": {
                "error": True,
                "error_message": str(e) # ACTUAL ERROR REASON
            }
        }
        print("sending", response)
        encrypted_response = encrypt_payload(response)
        return PlainTextResponse(content=encrypted_response, media_type='text/plain')

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """
    Standard webhook to receive the final flow completion message (nfm_reply).
    """
    try:
        body = await request.json()
        
        # Parse the standard WhatsApp Cloud API webhook structure
        if "entry" in body:
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for message in value.get("messages", []):
                            if message.get("type") == "interactive":
                                interactive = message.get("interactive", {})
                                if interactive.get("type") == "nfm_reply":
                                    # The final flow JSON response is here
                                    nfm_reply = interactive.get("nfm_reply", {})
                                    response_json_str = nfm_reply.get("response_json")
                                    if response_json_str:
                                        flow_data = json.loads(response_json_str)
                                        handle_submission(flow_data)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
