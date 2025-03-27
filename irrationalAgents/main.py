'''
Author: Yifei Wang
Github: ephiewangyf@gmail.com
Date: 2025-03-25 20:41:31
LastEditors: ephie && ephiewangyf@gmail.com
LastEditTime: 2025-03-25 20:56:55
FilePath: /Agents-Sim/irrationalAgents/main.py
Description: 
'''
from API.unity import UnityServer

def main():
    server = UnityServer()
    if server.run():
        server.keep_alive()

if __name__ == '__main__':
    main()
