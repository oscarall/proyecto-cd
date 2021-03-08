import socket
import jsons


def start_socket(lamport_handler):
    TIME = 0
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
                TIME = max(time, TIME) + 1
                lamport_handler.external_request(msg)
            
            reply = msg.get("reply")
            if reply:
                lamport_handler.reply()
            
            release = msg.get("release", None)
            if release:
                lamport_handler.release_request(msg)

    except KeyboardInterrupt:
        print('Exiting')