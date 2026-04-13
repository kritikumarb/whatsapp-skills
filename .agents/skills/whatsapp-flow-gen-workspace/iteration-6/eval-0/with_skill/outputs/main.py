from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Stubs) ---
def decrypt_payload(body_dict):
    """Decrypts Flow Endpoint requests. (Stub for implementation)"""
    return body_dict

def encrypt_payload(response_dict):
    """Encrypts Flow Endpoint responses. (Stub for implementation)"""
    return json.dumps(response_dict)

# --- Business Logic ---
def handle_submission(flow_data):
    """
    Processes the final flow completion data.
    """
    print(f"Final Flow Data Received: {flow_data}")
    # In a real app, you might save this to a database
    return {"status": "success"}

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
        # Check for the mandatory trigger name
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "submit_survey":
            user_name = data.get("name", "User")
            favorite_fruit = data.get("fruit", "fruit")
            
            # Transition to success screen with personalized message
            response_data["screen"] = "SUCCESS_SCREEN_RESERVED"
            response_data["data"] = {
                "message": f"Hi {user_name}! We've recorded that your favorite fruit is {favorite_fruit}. Thank you for your feedback!"
            }
        else:
            # Fallback if trigger is unknown
            response_data["screen"] = "SUCCESS_SCREEN_RESERVED"
            response_data["data"] = {"message": "Thank you for your response!"}
            
    # Note: In production, this would return an encrypted string
    # For this exercise, we return the JSON string as per stub
    encrypted_response = encrypt_payload(response_data)
    return Response(content=encrypted_response, media_type="text/plain")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """Standard webhook to receive the final flow completion message."""
    body = await request.json()
    
    # Process messages -> interactive -> nfm_reply (Flow response)
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            for message in messages:
                if message.get("type") == "interactive":
                    interactive = message.get("interactive", {})
                    if interactive.get("type") == "nfm_reply":
                        # The final flow JSON is here
                        response_json = interactive.get("nfm_reply", {}).get("response_json")
                        flow_data = json.loads(response_json)
                        handle_submission(flow_data)
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
