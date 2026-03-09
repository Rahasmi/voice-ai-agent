import asyncio
import websockets

async def chat():
    uri = "ws://127.0.0.1:8000/ws"

    try:
        async with websockets.connect(uri) as websocket:
            while True:
                text = input("You: ").strip()

                if not text:
                    continue

                if text.lower() == "exit":
                    print("Closing chat...")
                    break

                await websocket.send(text)

                try:
                    response = await websocket.recv()
                    print("Agent:", response)
                except websockets.exceptions.ConnectionClosedError as e:
                    print("Connection closed by server:", e)
                    break

    except Exception as e:
        print("Could not connect to websocket:", e)

asyncio.run(chat())