import socketio
import eventlet
import logging

# Configure logging
logging.basicConfig(
    filename='server.log',  # Log file name
    level=logging.INFO,     # Log level (INFO, DEBUG, ERROR, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
)

# Create a Socket.IO server with CORS allowed
sio = socketio.Server(cors_allowed_origins="*")

# Wrap the server with a WSGI application
app = socketio.WSGIApp(sio)

# Define events
@sio.event
def connect(sid, environ):
    logging.info(f"Client connected: {sid}")
    sio.emit("command.map.GetMapTown", '', to=sid)

@sio.on('command.map.GetMapTown')
def handle_get_map_scene(sid, data):
    logging.info(f"Received command.map.GetMapScene from {sid}: {data}")
    # Process the received data and respond if necessary
    sio.emit("response.map.GetMapScene", {"status": "success", "data": data}, to=sid)

@sio.event
def disconnect(sid):
    logging.info(f"Client disconnected: {sid}")

@sio.on('message')
def handle_message(sid, data):
    logging.info(f"Message from {sid}: {data}")
    sio.emit("message_response", f"Echo: {data}", to=sid)

# Run the server
if __name__ == "__main__":
    logging.info("Socket.IO server is starting on http://localhost:8080")
    eventlet.wsgi.server(eventlet.listen(('localhost', 8080)), app)