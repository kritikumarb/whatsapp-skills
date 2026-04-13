from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Provided by User) ---
def decrypt_payload(body_dict):
    """Decrypts Flow Endpoint requests."""
    # In production, implement actual decryption using the private key
    return body_dict

def encrypt_payload(response_dict):
    """Encrypts Flow Endpoint responses."""
    # In production, implement actual encryption using the session key
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    data = json.loads(flow_response_json)
    print(f"Final Flow Data Received: {data}")
    # ... Database storage or business logic ...
    return {"status": "success"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    screen = decrypted_data.get("screen")
    data = decrypted_data.get("data", {})
    
    response_data = {"version": "3.1"}
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "submit_survey":
             # Logic to transition to the SUMMARY_SCREEN
             response_data["screen"] = "SUMMARY_SCREEN"
             response_data["data"] = {
                 "name": data.get("name", "User"),
                 "favorite_fruit": data.get("favorite_fruit", "Unknown")
             }
        else:
             # Fallback
             response_data["screen"] = "SURVEY_SCREEN"
             response_data["data"] = {}
            
    encrypted_response = encrypt_payload(response_data)
    # Note: Content-Type should be text/plain for encrypted responses
    return Response(content=encrypted_response, media_type="text/plain")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Standard webhook to receive the final flow completion message."""
    body = await request.json()
    
    # Check for messages -> interactive -> nfm_reply (Flow response)
    if "entry" in body:
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
