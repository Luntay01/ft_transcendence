
print("WebSocket server - Work in Progress")
import asyncio
import websockets
#test

async def handler(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")

start_server = websockets.serve(handler, "0.0.0.0", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server running...")
asyncio.get_event_loop().run_forever()


#import asyncio
#import websockets
#
## List to keep track of connected clients
#connected_clients = set()
#
## Function to handle incoming WebSocket connections
#async def handle_client(websocket, path):
#    # Add the new client to the list
#    connected_clients.add(websocket)
#    print(f"New client connected. Total clients: {len(connected_clients)}")
#    
#    try:
#        # Keep receiving messages from this client
#        async for message in websocket:
#            print(f"Received message from client: {message}")
#            
#            # Broadcast the message to all connected clients
#            await broadcast(message)
#    except websockets.exceptions.ConnectionClosed as e:
#        print(f"Client disconnected: {e}")
#    finally:
#        # Remove the client from the set when they disconnect
#        connected_clients.remove(websocket)
#        print(f"Client disconnected. Total clients: {len(connected_clients)}")
#
## Function to send a message to all connected clients
#async def broadcast(message):
#    if connected_clients:  # Only broadcast if there are connected clients
#        await asyncio.wait([client.send(message) for client in connected_clients])
#
## Start the WebSocket server
#async def main():
#    async with websockets.serve(handle_client, "0.0.0.0", 8765):
#        print("WebSocket server started on ws://0.0.0.0:8765")
#        await asyncio.Future()  # Run forever
#
#if __name__ == "__main__":
#    asyncio.run(main())