from fastapi import FastAPI, Request, Response
import json
import base64

app = FastAPI()

# --- External Utilities (Simulated) ---
def decrypt_payload(body_dict):
    """
    In a real-world scenario, this would decrypt the Base64/encrypted payload 
    from WhatsApp using your Private Key. For this example, we assume 
    the body is already a JSON dictionary.
    """
    return body_dict

def encrypt_payload(response_dict):
    """
    In a real-world scenario, this would encrypt the response dictionary 
    and return it as a Base64 encoded string.
    """
    # For simulation, just return a base64 encoded JSON string
    json_str = json.dumps(response_dict)
    return base64.b64encode(json_str.encode()).decode()

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    # Parse the data from the flow
    # The 'response_json' is already a JSON string from 'nfm_reply'
    data = json.loads(flow_response_json)
    
    user_name = data.get("user_name")
    favorite_fruit = data.get("favorite_fruit")
    
    print(f"--- NEW SURVEY SUBMISSION ---")
    print(f"Name: {user_name}")
    print(f"Favorite Fruit: {favorite_fruit}")
    print(f"----------------------------")
    
    return {"status": "success", "user": user_name}

# --- Endpoints ---

@app.post("/whatsapp-flow")
async def handle_flow_endpoint(request: Request):
    """
    Encrypted endpoint for WhatsApp Flow interactions (ping, data_exchange).
    """
    body = await request.json()
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    screen = decrypted_data.get("screen")
    data = decrypted_data.get("data", {})
    
    response_data = {"version": "3.1"}
    
    if action == "ping":
        response_data["data"] = {"status": "active"}
    elif action == "data_exchange":
        # In this simple one-screen flow, 'data_exchange' might not be triggered 
        # unless there are intermediate validation steps or additional screens.
        # But we include the logic for completeness.
        response_data["screen"] = "SURVEY_SCREEN" # Stay or move
        response_data["data"] = {"message": "Data received"}
            
    encrypted_response = encrypt_payload(response_data)
    return Response(content=encrypted_response, media_type="text/plain")

@app.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """
    Standard webhook to receive the final flow completion message.
    WhatsApp sends an 'interactive' message of type 'nfm_reply'.
    """
    body = await request.json()
    
    # Iterate through the incoming message structure
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                if message.get("type") == "interactive":
                    interactive = message.get("interactive", {})
                    if interactive.get("type") == "nfm_reply":
                        # This is the final JSON payload from the 'complete' action in flow.json
                        response_json = interactive.get("nfm_reply", {}).get("response_json")
                        if response_json:
                            handle_submission(response_json)
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
