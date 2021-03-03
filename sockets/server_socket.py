from xmlrpc.server import SimpleXMLRPCServer
import logging
import os
import socket
from dotenv import load_dotenv
import json

load_dotenv()

HOST = os.getenv("SERVER_HOST", 'localhost')
PORT = os.getenv("SOCKET_PORT", 2016)

HOST_1 = SERVER_HOST_1 = os.getenv("SERVER_HOST_1")
PORT_1 = SERVER_PORT_1 = os.getenv("SOCKET_PORT_1")

VARIABLES = {
    "x":0,
    "y":0
}

SERVERS_IP = [HOST_1]


def add(value, target):
    target = target.lower()
    VARIABLES[target] = VARIABLES[target] + value
    return f"Operation completed (addition), new value = {VARIABLES[target]}"

def get(target):
    target = target.lower()
    return f"The value of {target} is: {VARIABLES[target]}"

def multiply(value, target):
    target = target.lower()
    VARIABLES[target] = VARIABLES[target] * value
    return f"Operation completed (multiplication), new value of {target} = {VARIABLES[target]}"

try:
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind((HOST, PORT))
    soc.listen(5)
    while True:
        conn, addr = soc.accept()
        print ("Got connection from", addr)
        msg = conn.recv(1024)
        if addr[0] not in SERVERS_IP:
            try:
                client_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket_1.connect((HOST_1, PORT_1))
                client_socket_1.send(msg)
                while True:
                    data = client_socket_1.recv(1026).decode()
                    client_socket_1.close()
            except:
                print("Impossible to connect to servers")
                print("Continuing execution")
        data = json.loads(msg.decode())
        action = data.get("action", None)
        value = data.get("value", 0)
        target = data.get("target", None)
        response = "Invalid function"
        if (action == "ADD"):
            response = add(value, target)
        elif (action == "MULTIPLY"):
            response = multiply(value, target)
        elif (action == "GET") :
            response = get(target)
        else: 
            break
        conn.sendall(response.encode())
        break

    conn.close()

except KeyboardInterrupt:
    print('Exiting')