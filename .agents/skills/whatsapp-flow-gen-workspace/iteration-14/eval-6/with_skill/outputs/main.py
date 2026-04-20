from fastapi import FastAPI, Request
import traceback
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/whatsapp-flow")
async def handle_flow(request: Request):
    try:
        body = await request.json()
        # In a real scenario, you would decrypt the request here
        # decrypted_data = decrypt(body['encrypted_flow_data'])
        decrypted_data = body # Simulating for this prototype
        
        action = decrypted_data.get("action")
        screen = decrypted_data.get("screen")
        
        if action == "ping":
            return {
                "version": "7.1",
                "data": {
                    "status": "active"
                }
            }
        
        if action == "data_exchange":
            # Handle data exchange logic if needed
            return {
                "screen": "VERIFICATION_SCREEN",
                "data": {}
            }
            
        return {
            "screen": "VERIFICATION_SCREEN",
            "data": {}
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "screen": screen if 'screen' in locals() else "VERIFICATION_SCREEN",
            "data": {
                "error": True,
                "error_message": str(e)
            }
        }

@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        # Process the final submission from the flow
        # In nfm_reply, the data is in messages[0].interactive.nfm_reply.response_json
        print("Received submission:", body)
        return {"status": "success"}
    except Exception as e:
        print(f"Error in webhook: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
