import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send some test heart rate data (e.g., "72,75,78,77,76")
        await websocket.send([40, 40, 40, 43, 46, 48, 48, 50, 51, 56, 58, 60, 60, 61, 61, 61])
        
        # Receive response from server
        response = await websocket.recv()
        print(f"Response from server: {response}")

asyncio.run(test_websocket())
