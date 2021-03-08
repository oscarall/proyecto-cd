import socket
import json
import os

HOST = os.getenv("SERVER_HOST", 'localhost')
PORT = int(os.getenv("SOCKET_PORT", 3000))

def start_socket(lamport_handler):
    print("Starting socket")
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.bind((HOST, PORT))
        soc.listen(5)
        while True:
            conn, addr = soc.accept()
            print ("Got connection from", addr)
            msg = json.loads(conn.recv(1024).decode('utf-8'))
            
            action = msg.get("action", None)
            if action:
                lamport_handler.external_request(msg)
            
            reply = msg.get("reply")
            if reply:
                id = msg.get("id")
                lamport_handler.reply(id)
            
            release = msg.get("release", None)
            if release:
                lamport_handler.release_request(msg)

    except KeyboardInterrupt:
        print('Exiting')