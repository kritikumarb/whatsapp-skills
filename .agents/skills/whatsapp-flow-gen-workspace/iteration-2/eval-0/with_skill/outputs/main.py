from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# These functions are assumed to be provided by the encryption layer/utilities
def decrypt_payload(body_dict):
    """
    Decrypts the incoming WhatsApp Flow request body.
    Placeholder: implementation should handle RSA-OAEP and AES-GCM.
    """
    return body_dict

def encrypt_payload(response_dict):
    """
    Encrypts the response payload and returns a Base64 string.
    Placeholder: implementation should handle AES-GCM encryption.
    """
    return json.dumps(response_dict)

@app.post("/whatsapp-flow")
async def handle_flow(request: Request):
    # 1. Get encrypted body from request
    body = await request.json()
    
    # 2. Decrypt the payload
    decrypted_data = decrypt_payload(body)
    
    action = decrypted_data.get("action")
    screen = decrypted_data.get("screen")
    data = decrypted_data.get("data", {})
    
    response_data = {"version": "3.1"}
    
    # 3. Handle Actions
    if action == "ping":
        # Health check
        response_data["data"] = {"status": "active"}
    
    elif action == "data_exchange":
        # Screen-specific logic
        if screen == "SURVEY":
            user_name = data.get("user_name", "User")
            favorite_fruit = data.get("favorite_fruit", "Fruit")
            
            # Transition to SUCCESS screen with dynamic data
            response_data["screen"] = "SUCCESS"
            response_data["data"] = {
                "success_message": f"Hi {user_name}! Your favorite fruit is {favorite_fruit}. Thank you for completing the survey!"
            }
        else:
            # Default fallback for data_exchange
            response_data["screen"] = "SUCCESS"
            response_data["data"] = {"success_message": "Success!"}
            
    # 4. Encrypt and return as Base64 string with Content-Type: text/plain
    encrypted_response = encrypt_payload(response_data)
    return Response(content=encrypted_response, media_type="text/plain")
