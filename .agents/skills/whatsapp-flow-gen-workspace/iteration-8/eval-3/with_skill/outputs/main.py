from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Simulated) ---
def decrypt_payload(body_dict):
    """
    In a real scenario, this would decrypt the body using the private key.
    For this example, we assume the body is already decrypted or handled by a middleware.
    """
    return body_dict

def encrypt_payload(response_dict):
    """
    In a real scenario, this would encrypt the response using the session key.
    For this example, we return the dict as a JSON string.
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
        print(f"Booking Confirmed: {data}")
        # Logic to save to database would go here
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Error processing submission: {e}")
        return {"status": "error", "message": str(e)}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
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
            
            if trigger == "fetch_times":
                # Business logic to fetch available times based on service and date
                service = data.get("service")
                date = data.get("date")
                
                # Mock data for available times
                available_times = [
                    {"id": "09:00", "title": "09:00 AM"},
                    {"id": "10:30", "title": "10:30 AM"},
                    {"id": "14:00", "title": "02:00 PM"},
                    {"id": "16:00", "title": "04:00 PM"}
                ]
                
                # Logic for showing notice (e.g., if it's a weekend)
                # Task says notice visible if show_notice is False.
                # So we set show_notice=False to show the notice.
                show_notice = False 
                
                response_data["screen"] = "SELECT_TIME"
                response_data["data"] = {
                    "service": service,
                    "date": date,
                    "available_times": available_times,
                    "show_notice": show_notice
                }
            else:
                response_data["screen"] = "SELECT_SERVICE"
                response_data["data"] = {"error": "Invalid trigger"}
        
        # In a real implementation, this would be encrypted.
        return Response(content=encrypt_payload(response_data), media_type="application/json")
    
    except Exception as e:
        print(f"Endpoint Error: {e}")
        return Response(content=json.dumps({"error": str(e)}), status_code=500, media_type="application/json")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Standard webhook to receive the final flow completion message."""
    try:
        body = await request.json()
        
        # Navigate the nested structure to find nfm_reply
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
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
