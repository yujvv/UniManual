import asyncio
import websockets
import json

async def connect_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send a message
        message = input("Enter your message: ")
        await websocket.send(json.dumps({"message": message}))
        
        # Receive and print responses
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                print("Received:", data)
                
                # Check if this is the final message
                if "finish_reason" in data and data["finish_reason"] == "stop":
                    break
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

async def main():
    await connect_websocket()

if __name__ == "__main__":
    asyncio.run(main())