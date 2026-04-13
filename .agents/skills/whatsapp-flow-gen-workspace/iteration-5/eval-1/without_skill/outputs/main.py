from fastapi import FastAPI, Request
from typing import Dict, Any

app = FastAPI()

@app.post("/webhook")
async def handle_flow(request: Request):
    """
    Handles WhatsApp Flow data exchange and interactions.
    """
    body = await request.json()
    action = body.get("action")
    payload = body.get("payload", {})
    
    # In a real scenario, you'd verify the request signature here.

    if action == "ping":
        return {
            "data": {
                "status": "active"
            }
        }

    if action == "data_exchange":
        destination = payload.get("destination")
        
        # Mock seat data based on destination
        # In a real app, this would query a database.
        mock_seats = {
            "NYC": [
                {"id": "1A", "title": "1A (Window)"},
                {"id": "1B", "title": "1B (Aisle)"},
                {"id": "2A", "title": "2A (Window)"},
                {"id": "2B", "title": "2B (Aisle)"}
            ],
            "LON": [
                {"id": "5F", "title": "5F (Window)"},
                {"id": "5E", "title": "5E (Middle)"},
                {"id": "5D", "title": "5D (Aisle)"}
            ],
            "PAR": [
                {"id": "10A", "title": "10A (Window)"},
                {"id": "10C", "title": "10C (Aisle)"}
            ]
        }
        
        selected_seats = mock_seats.get(destination, [{"id": "GEN", "title": "General Seating"}])

        return {
            "screen": "screen_seat",
            "data": {
                "available_seats": selected_seats
            }
        }

    if action == "complete":
        # Final submission handling
        return {
            "data": {
                "status": "success",
                "message": f"Booking confirmed for {payload.get('destination')} at seat {payload.get('seat')}."
            }
        }

    return {"error": "Invalid action"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
