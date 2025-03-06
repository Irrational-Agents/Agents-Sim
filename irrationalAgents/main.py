from API.unity.unity import UnityServer
import eventlet

def main():
    unity_server = UnityServer()
    
    if unity_server.run():
        unity_server.keep_alive()

if __name__ == '__main__':
    main() 