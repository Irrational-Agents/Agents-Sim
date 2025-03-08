from typing import Dict, Callable, Optional, Any
from datetime import datetime
from logger_config import setup_logger
import socketio

# Setup the logger for this module
logger = setup_logger('API-unity-request')

class UnityRequest:
    """
    A class to manage communication with a Unity client via Socket.IO.

    Attributes:
        sio: The Socket.IO server instance.
        current_client_sid: The session ID of the current client.
    """

    def __init__(self, sio: socketio.AsyncServer, current_client_sid: str):
        """
        Initialize a UnityRequest instance.

        Args:
            sio: The Socket.IO server instance.
            current_client_sid: The session ID of the current client.
        """
        self.sio = sio
        self.current_client_sid = current_client_sid

    def emit(self, event_name: str, data: Optional[dict] = None) -> None:
        try:
            self.sio.emit(event_name, data, to=self.current_client_sid)
            logger.info(f"Emitted event '{event_name}' to client {self.current_client_sid}. Data: {data}")
        except Exception as e:
            logger.error(f"Error emitting event '{event_name}': {str(e)}")


    def send_init(self, request_data: Optional[dict] = None) -> None:
        """Send Init with npc data."""
        self.emit("init", request_data)      

    def send_server_tick(self, request_data: Optional[dict] = None) -> None:
        """Send Server tick for frame to be updated."""
        self.emit("server.tick", request_data)   

    def get_map_data(self, request_data: Optional[dict] = None) -> None:
        """Request town map data."""
        self.emit("map.getData", request_data)

    def npc_chat_update(self, request_data: Optional[dict] = None) -> None:
        """Update NPC chat data."""
        self.emit("chat.updateNPC", request_data)
