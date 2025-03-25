# Agents-Sim

Agents Sim repository

## Branches

- **main**: This is the production branch containing the latest stable release.
- **stage**: This branch is used for staging and pre-production testing.
- **develop**: This branch is for ongoing development and feature integration.

## Environments

- **Development**: [Dev Environment](https://agents-sim-dev-lo5zb4dpiq-ts.a.run.app)
- **Staging**: [Staging environment](https://agents-sim-stage-lo5zb4dpiq-ts.a.run.app)
- **Production**: [Main Environment](https://agents-sim-main-lo5zb4dpiq-ts.a.run.app)

### Code Running

1. Prepare api keys and set variables in ur environments.
   1. https://platform.openai.com/
   2. https://smith.langchain.com/
   
    ```
      OPENAI_API_KEY=""
      SOCKET_URL="https://orange-cliff-0b3a9151e.5.azurestaticapps.net:8080"
      WORK_DIR='{ur path}/irrationalAgents'
      LOG_LEVEL='DEBUG'
      LANGCHAIN_API_KEY=""
    ```
2. install 
   ```
   pip install -r requirements.txt
   ``` 

3. Entrence see test2.py (or you can make ur own)
   ```
   python test3.py
<<<<<<< HEAD
   ```
=======
   ```


### Dev

#### QuickStart

```
cd irrationalAgents
python main.py
```

~~APIs~~
```
ui.tick
server.tick

player.getInfo
player.getInfo.response

npc.getList
npc.getList.response

npc.getInfo
npc.getInfo.response

npc.navigate

map.getTownData
map.getTownData.response

map.getSceneMetadata
map.getSceneMetadata.response

config.getBlockData
config.getBlockData.response

chat.updateNPC
```
>>>>>>> 81cbe8af04df36294672062a0d14b8afff8cd420
