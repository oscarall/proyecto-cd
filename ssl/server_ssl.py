import socket
import socketserver
import ssl
import pickle
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, SimpleXMLRPCRequestHandler
import mysql.connector
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

load_dotenv()
try:
    import fcntl
except ImportError:
    fcntl = None

KEYFILE = 'privatekey.pem'    # Replace with your PEM formatted key file
CERTFILE = 'cert.pem'  # Replace with your PEM formatted certificate

mydb = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', 'root'),
    database=os.getenv('DATABASE', '')
)

USER = 'test'
PASSWORD = os.environ.get('PASSWORD')
SERVER_HOST = os.getenv("SERVER_HOST", 'localhost')

userPassDict = {USER: PASSWORD}


class SimpleXMLRPCServerTLS(SimpleXMLRPCServer):
    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=True, allow_none=True, encoding=None, bind_and_activate=True):
        """Overriding __init__ method of the SimpleXMLRPCServer

        The method is an exact copy, except the TCPServer __init__
        call, which is rewritten using TLS
        """
        self.logRequests = logRequests

        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding)

        class VerifyingRequestHandler(SimpleXMLRPCRequestHandler):
            '''
            Request Handler that verifies username and password passed to
            XML RPC server in HTTP URL sent by client.
            '''
            # this is the method we must override

            def parse_request(self):
                # first, call the original implementation which returns
                # True if all OK so far
                if SimpleXMLRPCRequestHandler.parse_request(self):
                    # next we authenticate
                    if self.authenticate(self.headers):
                        return True
                    else:
                        # if authentication fails, tell the client
                        self.send_error(401, 'Authentication failed')
                return False

            def authenticate(self, headers):
                from base64 import b64decode
                #    Confirm that Authorization header is set to Basic
                (basic, _, encoded) = headers.get(
                    'Authorization').partition(' ')
                assert basic == 'Basic', 'Only basic authentication supported'

                #    Encoded portion of the header is a string
                #    Need to convert to bytestring
                encodedByteString = encoded.encode()
                #    Decode Base64 byte String to a decoded Byte String
                decodedBytes = b64decode(encodedByteString)
                #    Convert from byte string to a regular String
                decodedString = decodedBytes.decode()
                #    Get the username and password from the string
                (username, _, password) = decodedString.partition(':')
                #    Check that username and password match internal global dictionary
                if username in userPassDict:
                    if userPassDict[username] == password:
                        return True
                return False

        #    Override the normal socket methods with an SSL socket
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

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)

# Restrict to a particular path.


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def executeRpcServer():
    # Create server
    server = SimpleXMLRPCServerTLS(
        (SERVER_HOST, 443), requestHandler=RequestHandler)
    server.register_introspection_functions()

    # Register an instance; all the methods of the instance are
    # published as XML-RPC methods (in this case, just 'div').

    class MyFuncs:
        def create_student(self, name, email):
            sql = "INSERT INTO ITAM.STUDENTS(name, email) values(%s, %s)"
            values = (name, email)
            cursor = mydb.cursor()
            cursor.execute(sql, values)
            mydb.commit()
            return {
                "status": "ok",
                "data": {
                    "id": cursor.lastrowid
                }
            }

        def get_student(self, id):
            sql = "SELECT * FROM ITAM.STUDENTS WHERE id = %s"
            values = (id,)
            cursor = mydb.cursor()
            cursor.execute(sql, values)
            student = cursor.fetchone()
            return {
                "status": "ok",
                "data": {
                    "id": student[0],
                    "name": student[1],
                    "email": student[2],
                    "created_date": student[3].strftime('%d-%m-%Y') if student[3] else student[3],
                    "updated_date": student[4].strftime('%d-%m-%Y') if student[4] else student[4],
                    "is_active": student[5]
                }
            }

        def disable_student(self, id):
            sql = "UPDATE ITAM.STUDENTS SET is_active = 0 WHERE id = %s"
            values = (id,)
            cursor = mydb.cursor()
            cursor.execute(sql, values)
            mydb.commit()

            return {
                "status": "OK",
                "data": {
                    "rowsAffected": cursor.rowcount
                }
            }

        def update_student(self, id, name, email):
            sql = "UPDATE ITAM.STUDENTS SET name = %s, email = %s, updated_date = NOW() WHERE id = %s"
            values = (name, email, id)
            cursor = mydb.cursor()
            cursor.execute(sql, values)
            mydb.commit()

            return {
                "status": "OK",
                "data": {
                    "rowsAffected": cursor.rowcount
                }
            }

    server.register_instance(MyFuncs())

    # Run the server's main loop
    print("Starting XML RPC Server")
    server.serve_forever()


if __name__ == '__main__':
    try:
        executeRpcServer()
    except KeyboardInterrupt:
        print('Exiting')
