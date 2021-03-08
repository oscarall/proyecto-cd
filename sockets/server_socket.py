from lamport import LamportHandler
from rpc import start_rpc_server
from sockets import start_socket
from multiprocessing.managers import BaseManager
from multiprocessing import Process
import os

nodes = {
    "148.205.36.203": 1026
}

def LamportHandlerProxy():
    return LamportHandler(nodes, "208")

def start_server():
    BaseManager.register("LamportHandler", LamportHandlerProxy)
    manager = BaseManager(address=("148.205.36.208", 1234))
    manager.start()
    lamport_handler = manager.LamportHandler() 

    try:
        rpc_server = Process(target=start_rpc_server, args=(lamport_handler,))
        socket_process = Process(target=start_socket, args=(lamport_handler,))
        rpc_server.start()
        socket_process.start()
        rpc_server.join()
        socket_process.join()
    except KeyboardInterrupt:
        print('Exiting')
          

if __name__ == '__main__': 
    start_server()
