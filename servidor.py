# servidor.py
import socket
import threading
import librosa
import pickle
import struct
import zlib
import time

HOST = '0.0.0.0'
PORT = 5050
CHUNK_SIZE = 2048

# Carrega áudio
audio_data, sr = librosa.load('musica.mp3', sr=None)
print(f"Áudio carregado: {len(audio_data)/sr:.2f} segundos, SR: {sr}")

# Cliente individual
def handle_client(conn, addr):
    print(f"[+] Cliente conectado: {addr}")
    try:
        conn.sendall(struct.pack('I', sr))  # Sample rate

        total_samples = len(audio_data)
        index = 0

        while index < total_samples:
            end = min(index + CHUNK_SIZE, total_samples)
            chunk = audio_data[index:end]

            data = pickle.dumps(chunk)
            compressed = zlib.compress(data)
            size = struct.pack('I', len(compressed))
            conn.sendall(size + compressed)

            index = end
            time.sleep(CHUNK_SIZE / sr)
    except Exception as e:
        print(f"[!] Erro com cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Cliente {addr} desconectado")

# Socket principal
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"[Servidor] Ouvindo em {HOST}:{PORT}")

try:
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
except KeyboardInterrupt:
    print("\nServidor encerrado.")
finally:
    server_socket.close()
