# cliente.py
import socket
import pickle
import struct
import zlib
import sounddevice as sd
import numpy as np
import threading

SERVER_IP = '127.0.0.1'  # Use o IP do servidor (localhost para testar local)
PORT = 5050

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
print("[Cliente] Conectado.")

# Sample rate
sr_data = client_socket.recv(4)
sr = struct.unpack('I', sr_data)[0]
print(f"Sample rate: {sr}")

buffer = []
play_flag = True
stop_flag = False

# Thread: entrada de comandos
def command_input():
    global play_flag, stop_flag
    while True:
        cmd = input("Comando (p=pause, r=resume, s=stop): ").strip().lower()
        if cmd == 'p':
            play_flag = False
        elif cmd == 'r':
            play_flag = True
        elif cmd == 's':
            stop_flag = True
            break

# Callback de áudio
def audio_callback(outdata, frames, time_info, status):
    if not play_flag or len(buffer) < frames:
        outdata[:] = np.zeros((frames, 1))
    else:
        outdata[:] = np.array(buffer[:frames]).reshape(-1, 1)
        del buffer[:frames]

# Inicia stream
stream = sd.OutputStream(channels=1, samplerate=sr, callback=audio_callback)
stream.start()

# Inicia thread de comandos
threading.Thread(target=command_input, daemon=True).start()

try:
    while not stop_flag:
        size_data = client_socket.recv(4)
        if not size_data:
            break
        block_size = struct.unpack('I', size_data)[0]

        block_data = b''
        while len(block_data) < block_size:
            packet = client_socket.recv(block_size - len(block_data))
            if not packet:
                break
            block_data += packet

        decompressed = zlib.decompress(block_data)
        chunk = pickle.loads(decompressed)
        buffer.extend(chunk.tolist())
except Exception as e:
    print(f"[!] Erro: {e}")
finally:
    stream.stop()
    client_socket.close()
    print("Cliente encerrado.")
