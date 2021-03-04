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
PORT = os.getenv("SOCKET_PORT", 3000)

USER = os.getenv("SSL_NAME")
PASSWORD = os.getenv('PASSWORD')
SERVER_HOST = os.getenv("SERVER_HOST", 'localhost')
KEYFILE = 'privatekey.pem'    # Replace with your PEM formatted key file
CERTFILE = 'cert.pem'  # Replace with your PEM formatted certificate
userPassDict = {USER: PASSWORD}
HOST_1 = SERVER_HOST_1 = os.getenv("SERVER_HOST_1")
PORT_1 = SERVER_PORT_1 = os.getenv("SOCKET_PORT_1")

VARIABLES = {
    "x":0,
    "y":0
}

SERVERS_IP = [HOST_1]


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
                print(userPassDict)
                print(username)
                print(password)
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

def send_socket_msg(msg):
    client_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket_1.connect((HOST_1, 1026))
    client_socket_1.send(str.encode(msg))
    data = client_socket_1.recv(1026).decode()
    client_socket_1.close()
    

def executeRpcServer():
    server = SimpleXMLRPCServerTLS(
        (SERVER_HOST, 443), requestHandler=RequestHandler)
    server.register_introspection_functions()

    class MyFuncs:
        def add(self, target, value):
            response = add_value(value, target)
            print(response)
            payload = {
                "target": target,
                "value": value,
                "action": "ADD"
            }
            send_socket_msg(json.dumps(payload))

        def multiply(self, target, value):
            response = multiply_value(value, target)
            print(response)
            payload = {
                "target": target,
                "value": value,
                "action": "MULTIPLY"
            }
            send_socket_msg(json.dumps(payload))
        
        def get(self, target):
            return get_value(target)


    server.register_instance(MyFuncs())

    print("Starting XML RPC Server")
    server.serve_forever()

def add_value(value, target):
    target = target.lower()
    VARIABLES[target] = VARIABLES[target] + value
    response = f"Operation completed (addition), new value of {target} = {VARIABLES[target]}"
    print(response)
    return response

def get_value(target):
    target = target.lower()
    return f"The value of {target} is: {VARIABLES[target]}"

def multiply_value(value, target):
    target = target.lower()
    VARIABLES[target] = VARIABLES[target] * value
    response = f"Operation completed (multiplication), new value of {target} = {VARIABLES[target]}"
    print(response)
    return response


def create_socket():
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.bind((HOST, PORT))
        soc.listen(5)
        while True:
            conn, addr = soc.accept()
            print ("Got connection from", addr)
            msg = conn.recv(1024)
            data = json.loads(msg.decode())
            action = data.get("action", None)
            value = data.get("value", 0)
            target = data.get("target", None)
            response = "Invalid function"
            if (action == "ADD"):
                response = add_value(value, target)
            elif (action == "MULTIPLY"):
                response = multiply_value(value, target)
            elif (action == "GET") :
                response = get_value(target)
            else: 
                break
            print(response)
            conn.sendall(response.encode())

    except KeyboardInterrupt:
        print('Exiting')


def start_server(): 
    n = os.fork() 
   
    if n > 0: 
        print("Parent process and id is : ", os.getpid())
        executeRpcServer() 
    else: 
        print("Child process and id is : ", os.getpid())
        create_socket()
          

if __name__ == '__main__': 
    start_server()
