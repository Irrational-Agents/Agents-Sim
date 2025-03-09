from API.unity import UnityServer
from config.config import load_config_to_env

def main():
    unity_server = UnityServer()
    
    if unity_server.run():
        unity_server.keep_alive()

if __name__ == '__main__':

    load_config_to_env()
    main() 