import asyncio
import websockets
import json

current_track = None #A track que está sendo tocada no momento
playback_position = 0 #A posição atual do playback da track (em segundos)
is_playing = False #Se a música está tocando ou pausada
clients = set() #Um conjunto para armazenar os clientes conectados

async def handle_client(websocket): #Método chamado toda vez que um novo cliente se conecta ao server
    #Adiciona o novo cliente ao conjunto de clientes conectados
    clients.add(websocket)
    try:
        #Envia o estado atual ao novo cliente
        await websocket.send(json.dumps({
            "track": current_track,
            "position": playback_position,
            "is_playing": is_playing
        }))
        
        #Escuta por mensagens do cliente
        async for message in websocket:
            data = json.loads(message) #Converte a mensagem que chega
            if data["action"] == "play":
                #Atualiza o estado global e o transmite a todos os clientes
                await broadcast({"action": "play", "track": data["track"]})
            elif data["action"] == "pause":
                await broadcast({"action": "pause"})
            elif data["action"] == "seek":
                await broadcast({"action": "seek", "position": data["position"]})
    finally:
        #Remove o cliente quando ele se desconecta
        clients.remove(websocket)
        
async def broadcast(message): #Método que envia uma mensagem para todos os clientes conectados
    for client in clients:
        await client.send(json.dumps(message))

async def main():
    #Inicia o servidor WebSocket
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server started at ws://localhost:8765")
        await asyncio.Future() #É executado indefinidamente

#Executa o server
asyncio.run(main())