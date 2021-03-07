from datetime import datetime
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, SimpleXMLRPCRequestHandler
import logging
import os
import socket
from dotenv import load_dotenv
import json
import ssl
import socketserver


try:
    import fcntl
except ImportError:
    fcntl = None

load_dotenv()

HOST = os.getenv("SERVER_HOST", 'localhost')
PORT = int(os.getenv("SOCKET_PORT", 3000))

USER = os.getenv("SSL_NAME")
PASSWORD = os.getenv('PASSWORD')
KEYFILE = 'privatekey.pem'    # Replace with your PEM formatted key file
CERTFILE = 'cert.pem'  # Replace with your PEM formatted certificate
userPassDict = {USER: PASSWORD}
HOST_1 = os.getenv("SERVER_HOST_1")
PORT_1 = int(os.getenv("SOCKET_PORT_1"))

VARIABLES = {
    "x":0,
    "y":0
}

TIME = 0

SERVERS = {f"{HOST_1}": PORT_1}
ID = HOST.split('.')[3]

REQUEST_QUEUE = []
REPLIES = 0


class SimpleXMLRPCServerTLS(SimpleXMLRPCServer):
    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=True, allow_none=True, encoding=None, bind_and_activate=True):
        self.logRequests = logRequests

        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding)

        class VerifyingRequestHandler(SimpleXMLRPCRequestHandler):
            def parse_request(self):
                if SimpleXMLRPCRequestHandler.parse_request(self):
                    if self.authenticate(self.headers):
                        return True
                    else:
                        self.send_error(401, 'Authentication failed')
                return False

            def authenticate(self, headers):
                from base64 import b64decode

                (basic, _, encoded) = headers.get('Authorization').partition(' ')
                assert basic == 'Basic', 'Only basic authentication supported'

                encodedByteString = encoded.encode()
                decodedBytes = b64decode(encodedByteString)
                decodedString = decodedBytes.decode()
                (username, _, password) = decodedString.partition(':')

                if username in userPassDict:
                    if userPassDict[username] == password:
                        return True
                return False
        socketserver.BaseServer.__init__(self, addr, VerifyingRequestHandler)
        self.socket = ssl.wrap_socket(
            socket.socket(self.address_family, self.socket_type),
            server_side=True,
            keyfile=KEYFILE,
            certfile=CERTFILE,
            cert_reqs=ssl.CERT_NONE,
            ssl_version=ssl.PROTOCOL_TLSv1,
        )
        if bind_and_activate:
            self.server_bind()
            self.server_activate()

        """End of modified part"""

        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

def increment_timer():
    global TIME
    TIME = TIME + 1

def remove_request(ip):
    global REQUEST_QUEUE
    sender = ip.split('.')[3]
    for x in range(0, REQUEST_QUEUE):
        if REQUEST_QUEUE[x].sender == sender:
            REQUEST_QUEUE.pop(x)
            break

def push_request(request):
    REQUEST_QUEUE.append(request)

def send_socket_msg(msg):
    print("Message: ", msg)
    for key, value in SERVERS.items():
        print("Sending message to ", key)
        client_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket_1.connect((key, value))
        client_socket_1.send((msg+'\n').encode('utf-8'))
        data = json.loads(client_socket_1.recv(1026).decode('utf-8'))
        if "reply" in data:
            global REPLIES
            REPLIES = REPLIES + 1
        client_socket_1.close()
    
def send_reply(msg, ip):
    client_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket_1.connect((ip, SERVERS[ip]))
    client_socket_1.send((msg+'\n').encode('utf-8'))
    data = json.loads(client_socket_1.recv(1026).decode('utf-8'))
    client_socket_1.close()

def executeRpcServer():
    server = SimpleXMLRPCServerTLS(
        (HOST, 443), requestHandler=RequestHandler)
    server.register_introspection_functions()

    class MyFuncs:
        def add(self, target, value):
            increment_timer()
            payload = {
                "target": target,
                "value": value,
                "action": "ADD",
                "sender": ID,
                "time": TIME
            }
            push_request(payload)
            send_socket_msg(json.dumps(payload))

        def multiply(self, target, value):
            increment_timer()
            payload = {
                "target": target,
                "value": value,
                "action": "MULTIPLY",
                "sender": ID,
                "time": TIME
            }
            send_socket_msg(json.dumps(payload))
        
        def get(self, target):
            increment_timer()
            return get_value(target)


    server.register_instance(MyFuncs())

    print("Starting XML RPC Server")
    server.serve_forever()

def add_value(value, target):
    target = target.lower()
    VARIABLES[target] = VARIABLES[target] + value
    response = f"Operation completed (addition), new value of {target} = {VARIABLES[target]}"
    return response

def get_value(target):
    target = target.lower()
    return f"The value of {target} is: {VARIABLES[target]}"

def multiply_value(value, target):
    target = target.lower()
    VARIABLES[target] = VARIABLES[target] * value
    response = f"Operation completed (multiplication), new value of {target} = {VARIABLES[target]}"
    return response


def create_socket():
    global TIME
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.bind((HOST, PORT))
        soc.listen(5)
        while True:
            conn, addr = soc.accept()
            print ("Got connection from", addr)
            msg = json.loads(conn.recv(1024).decode('utf-8'))
            action = msg.get("action", None)
            value = msg.get("value", 0)
            target = msg.get("target", None)
            time = msg.get("time", 0)
            if action:
                TIME = max(time, TIME) + 1
                push_request(msg)
                response = {
                    "reply": "reply",
                    "id": ID,
                    "time": TIME
                }
                send_reply(json.dumps(response), addr[0])
                continue
            release = msg.get("release", None)
            if release:
                remove_request(addr[0])
            response = "Invalid function"
            if (action == "ADD"):
                response = add_value(value, target)
            elif (action == "MULTIPLY"):
                response = multiply_value(value, target)
            elif (action == "GET"):
                response = get_value(target)
            else:
                break
            print(response)
            conn.sendall(response.encode())

    except KeyboardInterrupt:
        print('Exiting')


def start_server(): 
    n = os.fork() 
    try:
        if n > 0: 
            print("Parent process and id is : ", os.getpid())
            executeRpcServer() 
        else:
            print("Child process and id is : ", os.getpid())
            create_socket()
    except KeyboardInterrupt:
        print('Exiting')
          

if __name__ == '__main__': 
    start_server()
