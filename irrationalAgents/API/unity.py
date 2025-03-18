import socketio
import asyncio
from API.handler import UnityHandlers
from API.request import UnityRequest
from unity_modules.tools import *
import json
import uvicorn
from config.logger_config import setup_logger

logger = setup_logger('API-unity')

class UnityServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.app = socketio.ASGIApp(self.sio)
        
        # State variables
        self.current_client_sid = None
        
        # Dependency initialization
        self.handlers = UnityHandlers()
        self.connected_event = asyncio.Event() 
        self.map_translator = None
        self.unity_request = None
        
        # Command mappings
        self.command_map = {
            'player.getInfo': 'handle_get_player_info',
            'npc.getList': 'handle_get_npc_list',
            'npc.getInfo': 'handle_get_npc_info',
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
            async def event_handler(sid, data, command=command, handler_name=handler_name):
                handler = getattr(self.handlers, handler_name, None)
                if handler:
                    logger.info(f"Received command: {command}")
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                else:
                    logger.info(f"No handler found for command: {command}")

    async def on_connect(self, sid, environ):
        """Handle a new client connection."""
        self.current_client_sid = sid
        self.unity_request = UnityRequest(self.sio, self.current_client_sid)
        logger.info(f"Client connected: {sid}")
        self.connected_event.set()  # 使用 set() 替代 send()

    async def on_disconnect(self, sid):
        """Handle client disconnection."""
        if sid == self.current_client_sid:
            self.current_client_sid = None
            self.unity_request = None
            logger.info(f"Client disconnected: {sid}")
            self.connected_event.clear()

    async def wait_for_connection(self, timeout=60) -> bool:
        """Wait for a client connection within the specified timeout."""
        logger.debug(f"Waiting for client connection with timeout: {timeout}s")
        try:
            await asyncio.wait_for(self.connected_event.wait(), timeout)
            self.handlers.unity_request = self.unity_request
            logger.info("Client connected successfully.")
            return True
        except asyncio.TimeoutError:
            logger.warning("Connection timeout exceeded.")
            return False

    async def init(self):
        """Perform server initialization tasks."""
        logger.info("Initializing server...")
        
        sim_config = {'npcs': get_npcs({})}
        npc_config = get_spawns()
        meta_config = get_meta()
        await self.unity_request.send_init(json.dumps({**sim_config, **npc_config, **meta_config}))

    async def start(self, host: str = '0.0.0.0', port: int = 8080):
        """Start the Unity server."""
        logger.info(f"Starting Unity server on {host}:{port}")
        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()

    async def keep_alive(self):
        """保持服务器运行"""
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down server...")

    async def run(self):
        """运行服务器的主要逻辑"""
        try:
            # 创建所有任务
            server_task = asyncio.create_task(self.start())
            keep_alive_task = asyncio.create_task(self.keep_alive())
            
            # 等待连接
            logger.info("Waiting for client connection...")
            if await self.wait_for_connection(timeout=30):
                await self.init()
                logger.info("Client connected, sending map request...")
                await self.unity_request.get_map_data()
                
                # 等待任务完成
                await asyncio.gather(server_task, keep_alive_task)
                return True
            else:
                logger.error("Timeout waiting for client connection.")
                return False
                
        except Exception as e:
            logger.error(f"Server error: {e}")
            return False
        finally:
            # 清理任务
            for task in [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

       