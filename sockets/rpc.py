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

USER = "test"
PASSWORD = "test"
KEYFILE = 'sockets/privatekey.pem'    # Replace with your PEM formatted key file
CERTFILE = 'sockets/cert.pem'  # Replace with your PEM formatted certificate
userPassDict = {USER: PASSWORD}


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

def start_rpc_server(lamport_handler):
    server = SimpleXMLRPCServerTLS(
        (HOST, 443), requestHandler=RequestHandler)
    server.register_introspection_functions()

    class MyFuncs:
        def add(self, target, value):
            payload = {
                "target": target,
                "value": value,
                "action": "ADD"
            }
            lamport_handler.request_mutual_exclusion(payload)

        def multiply(self, target, value):
            payload = {
                "target": target,
                "value": value,
                "action": "MULTIPLY"
            }
            lamport_handler.request_mutual_exclusion(payload)
        
        def get(self, target):
            return lamport_handler.get(target)


    server.register_instance(MyFuncs())

    print("Starting XML RPC Server")
    server.serve_forever()
