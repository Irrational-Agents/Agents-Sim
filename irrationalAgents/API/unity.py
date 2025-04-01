import socketio
import eventlet
from API.handler import UnityHandlers
from API.request import UnityRequest
from unity_modules.tools import *
import json

from config.logger_config import setup_logger

logger = setup_logger('API-unity')


class UnityServer:
    def __init__(self):
        # Initialize socket.io server with CORS support
        self.sio = socketio.Server(cors_allowed_origins='*')
        self.app = socketio.WSGIApp(self.sio)
        
        # State variables
        self.current_client_sid = None
        
        # Dependency initialization
        self.handlers = UnityHandlers()
        self.connected_event = eventlet.Event()
        self.map_translator = None
        self.unity_request = None
        
        # Command mappings
        self.command_map = {
            'map.data': 'handle_map_data',
            'ui.tick': 'update'
        }
        # Register event handlers
        self.register_event_handlers()

    def register_event_handlers(self):
        """Register all socket.io event handlers."""
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        
        for command, handler_name in self.command_map.items():
            @self.sio.on(command)
            def event_handler(_, data, command=command, handler_name=handler_name):
                handler = getattr(self.handlers, handler_name, None)
                if handler:
                    logger.info(f"Received command: {command}")
                    handler(data)
                else:
                    logger.info(f"No handler found for command: {command}")


    def on_connect(self, sid, _):
        """Handle a new client connection."""
        self.current_client_sid = sid
        self.unity_request = UnityRequest(self.sio, self.current_client_sid)
        self.handlers.unity_request = self.unity_request
        logger.info(f"Client connected: {sid}")
        if not self.connected_event.ready():
            self.connected_event.send(True)

    def on_disconnect(self, sid):
        """Handle client disconnection."""
        if sid == self.current_client_sid:
            self.current_client_sid = None
            self.unity_request = None
            self.handlers.unity_request = None
            logger.info(f"Client disconnected: {sid}")

    def wait_for_connection(self, timeout=60) -> bool:
        """Wait for a client connection within the specified timeout."""
        logger.debug(f"Waiting for client connection with timeout: {timeout}s")
        if self.connected_event.wait(timeout):
            self.handlers.unity_request = self.unity_request
            logger.info("Client connected successfully.")
            return True
        logger.warning("Connection timeout exceeded.")
        return False

    def start_background(self):
        """Start the server in the background."""
        return eventlet.spawn(self.start)

    def init(self):
        """Perform server initialization tasks."""
        logger.info("Initializing server...")
       
        sim_config = {'npcs': get_npcs({})}
        meta_config = get_meta()
        self.unity_request.send_init(json.dumps({**sim_config, **meta_config}))


    def start(self, host: str = '0.0.0.0', port: int = 8080):
        """Start the Unity server."""
        logger.info(f"Starting Unity server on {host}:{port}")
        eventlet.wsgi.server(eventlet.listen((host, port)), self.app)

    def keep_alive(self):
        try:
            while True:
                eventlet.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down server...")

    def run(self):
        self.start_background()

        logger.info("Waiting for client connection...")
        if self.wait_for_connection(timeout=120): 
            self.init() 
            logger.info("Client connected")
            return True
        else:
            logger.error("Timeout waiting for client connection.")
            return False
