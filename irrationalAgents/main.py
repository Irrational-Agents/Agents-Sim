from API.unity import UnityServer
from config import config
from config.logger_config import convert_log_level
import uvicorn

def main():
    server = UnityServer()
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=8080,
        log_level=convert_log_level(config.LOG_LEVEL, 'uvicorn')
    )

if __name__ == '__main__':

    main() 