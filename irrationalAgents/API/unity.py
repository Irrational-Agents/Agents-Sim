import os
import sys
import json
import socketio
import eventlet
from API.handler import UnityHandlers
from API.request import UnityRequest
from unity_modules.tools import *
from agents_modules.agent import get_agent_manager

from config.logger_config import setup_logger

logger = setup_logger('API-unity')


class UnityServer:
    def __init__(self):
        self.sio = socketio.Server(cors_allowed_origins='*')
        self.app = socketio.WSGIApp(self.sio)
        self.current_client_sid = None
        self.handlers = UnityHandlers()
        self.connected_event = eventlet.Event()
        self.map_translator = None
        self.unity_request = None

        self.command_map = {
            'map.data': 'handle_map_data',
            'ui.tick': 'update'
        }

        self.register_event_handlers()

    def register_event_handlers(self):
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('server.restart', self.on_restart)

        for command, handler_name in self.command_map.items():
            @self.sio.on(command)
            def event_handler(_, data, command=command, handler_name=handler_name):
                handler = getattr(self.handlers, handler_name, None)
                if handler is not None:
                    logger.debug(f"Received command: {command}")
                    handler(data)
                else:
                    logger.info(f"No handler found for command: {command}")

    def on_connect(self, sid, _):
        self.current_client_sid = sid
        self.unity_request = UnityRequest(self.sio, self.current_client_sid)
        self.handlers.unity_request = self.unity_request
        logger.info(f"Client connected: {sid}")
        if not self.connected_event.ready():
            self.connected_event.send(True)

    def on_disconnect(self, sid):
        if sid == self.current_client_sid:
            self.current_client_sid = None
            self.unity_request = None
            self.handlers.unity_request = None

        am = get_agent_manager()
        if hasattr(am, "save_agents"):
            logger.info("Saving agents and other data...")
            am.save_agents()  
        logger.info(f"Client disconnected: {sid}")

    def on_restart(self, sid):
        logger.info("Restart command received. Restarting server...")
        self.sio.emit('server.restarting', {
                      'message': 'Server is restarting...'}, room=sid)
        eventlet.sleep(1)
        os.execv(sys.executable, ['python'] + sys.argv)

    def wait_for_connection(self, timeout=60) -> bool:
        logger.debug(f"Waiting for client connection with timeout: {timeout}s")
        if self.connected_event.wait(timeout):
            self.handlers.unity_request = self.unity_request
            logger.info("Client connected successfully.")
            return True
        logger.warning("Connection timeout exceeded.")
        return False

    def start_background(self):
        return eventlet.spawn(self.start)

    def init(self):
        logger.info("Initializing server...")
        sim_config = {'npcs': get_npcs({})}
        meta_config = get_meta()
        self.unity_request.send_init(json.dumps({**sim_config, **meta_config}))

    def start(self, host: str = '0.0.0.0', port: int = 8080):
        logger.info(f"Starting Unity server on {host}:{port}")
        eventlet.wsgi.server(eventlet.listen((host, port)), self.app)

    def keep_alive(self):
        try:
            while True:
                eventlet.sleep(1)
        except KeyboardInterrupt:
            am = get_agent_manager()
            if hasattr(am, "save_agents"):
                logger.info("Saving agents and other data...")
                am.save_agents()
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
