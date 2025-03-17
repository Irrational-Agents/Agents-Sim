import socketio
import asyncio
import eventlet
from typing import Dict, Any
from logger_config import setup_logger
#from logger_config import setup_logger
from API.unity.handler import UnityHandlers
from API.unity.request import UnityRequest
from API.unity.config import Config

from datetime import datetime
import json


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
            'player.getInfo': 'handle_get_player_info',
            'npc.getList': 'handle_get_npc_list', #API
            'npc.getInfo': 'handle_get_npc_info', #API
            'map.data': 'handle_map_data',
            'ui.tick': 'update',
            'chat.updateNPC': 'handle_chat',
            'npc.navigate': 'handle_npc_navigate'
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
        logger.info(f"Client connected: {sid}")
        if not self.connected_event.ready():
            self.connected_event.send(True)

    def on_disconnect(self, sid):
        """Handle client disconnection."""
        if sid == self.current_client_sid:
            self.current_client_sid = None
            self.unity_request = None
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
       
        sim_name = "the_ville_test"
        sim_config = Config.get_sim_config(sim_name)
        npc_config = Config.get_spawn_config(sim_name)

        self.unity_request.send_init(json.dumps({**sim_config, **npc_config}))


    def start(self, host: str = '0.0.0.0', port: int = 8080):
        """Start the Unity server."""
        logger.info(f"Starting Unity server on {host}:{port}")
        eventlet.wsgi.server(eventlet.listen((host, port)), self.app)





if __name__ == '__main__':
    server = UnityServer()
    server.start_background()

    logger.info("Waiting for client connection...")
    if server.wait_for_connection(timeout=30): 
        server.init() 
        logger.info("Client connected, sending map request...")
    else:
        logger.error("Timeout waiting for client connection.")
    
    try:
        while True:
            eventlet.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")