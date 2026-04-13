# WhatsApp Flow Backend Reference (Comprehensive)

This reference demonstrates the decoupled architecture for handling both the WhatsApp Flow Endpoint (encrypted) and the standard Webhook (receiving the final response).

## Comprehensive Backend Pattern

```python
from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# --- External Utilities (Provided by User) ---
def decrypt_payload(body_dict):
    """Decrypts Flow Endpoint requests."""
    return body_dict

def encrypt_payload(response_dict):
    """Encrypts Flow Endpoint responses."""
    return "encrypted_base64_string"

# --- Business Logic ---
def handle_submission(flow_response_json):
    """
    Processes the final flow completion data.
    This logic runs when the 'complete' action is triggered.
    """
    # Parse the data from the flow
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
        # Check for the trigger name to identify the specific data exchange
        trigger = data.get("data_exchange_trigger")
        
        if trigger == "validate_user":
             response_data["screen"] = "SUCCESS_SCREEN"
             response_data["data"] = {"message": "User validated!"}
        else:
             response_data["screen"] = "DEFAULT_SUCCESS"
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
            messages = change.get("value", {}).get("messages", [])
            for message in messages:
                if message.get("type") == "interactive":
                    interactive = message.get("interactive", {})
                    if interactive.get("type") == "nfm_reply":
                        # The final flow JSON is here
                        response_json = interactive.get("nfm_reply", {}).get("response_json")
                        handle_submission(response_json)
    
    return {"status": "ok"}
```
