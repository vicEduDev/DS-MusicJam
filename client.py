import asyncio
import websockets
import json

async def client(): #Método que gerencia a conexão com o server e recebe/envia mensagens
    uri = "ws://localhost:8765" #Endereço do servidor WebSocket
    async with websockets.connect(uri) as websocket:
        #Recebe o estado inicial do servidor
        state = await websocket.recv()
        print("Initial state from server: ", state)
        
        #Simula as ações do usuário
        #Envia um comando de PLAY com o nome da track
        await websocket.send(json.dumps({"action": "play", "track": "song1.mp3"}))
        print("Sent play command")
        #Espera por 5 segundos
        await asyncio.sleep(5) 
        #Envia um comando de pause        
        await websocket.send(json.dumps({"action": "pause"}))
        print("Sent pause command")
        #Espera por 2 segundos
        await asyncio.sleep(2) 
        #Envia um comando de busca com a nova posição da track
        await websocket.send(json.dumps({"action": "seek", "position": 30}))
        print("Sent seek command")
    
#Executa o cliente
asyncio.run(client())