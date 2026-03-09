from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from agent.reasoning.process import process_request

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = process_request(data)
            await websocket.send_text(str(response))
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print("WebSocket error:", e)
        try:
            await websocket.send_text(f"Error: {str(e)}")
        except Exception:
            pass

@app.get("/")
def home():
    return {"message": "Voice AI Agent Running"}

@app.post("/chat")
def chat(message: str):
    response = process_request(message)
    return {"response": response}