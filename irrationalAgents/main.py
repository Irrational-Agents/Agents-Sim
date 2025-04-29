from API.unity import UnityServer

def main():
    server = UnityServer()
    if server.run():
        server.keep_alive()

if __name__ == '__main__':
    main()
