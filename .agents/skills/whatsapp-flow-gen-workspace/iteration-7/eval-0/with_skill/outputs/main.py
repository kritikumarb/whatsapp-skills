from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Provided by User) ---
def decrypt_payload(body_dict):
    """Decrypts Flow Endpoint requests."""
    # In a real implementation, decrypt the body using your private key
    return body_dict

def encrypt_payload(response_dict):
    """Encrypts Flow Endpoint responses."""
    # In a real implementation, encrypt the response using the session key
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    # Parse the data from the flow
    data = json.loads(flow_response_json)
    user_name = data.get("user_name")
    favorite_fruit = data.get("favorite_fruit")
    
    print(f"Survey Submission Received:")
    print(f"Name: {user_name}")
    print(f"Favorite Fruit: {favorite_fruit}")
    
    return {"status": "success", "message": f"Thank you, {user_name}!"}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """Encrypted endpoint for ping and data_exchange."""
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    # screen = decrypted_data.get("screen") # Not needed for simple complete flow
    data = decrypted_data.get("data", {})
    
    response_data = {"version": "3.0"} # data_api_version for endpoint
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        # Check for the trigger name to identify the specific data exchange
        trigger = data.get("data_exchange_trigger")
        
        # This simple flow doesn't use data_exchange, but we include the pattern
        if trigger == "validate_survey":
             response_data["screen"] = "SURVEY_SCREEN"
             response_data["data"] = {"message": "Data validated!"}
        else:
             response_data["screen"] = "SURVEY_SCREEN"
             response_data["data"] = {"message": "Data processed!"}
            
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
                        response_json = interactive.get("nfm_reply", {}).get("response_json")
                        handle_submission(response_json)
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
