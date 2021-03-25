from lamport import LamportHandler
from rpc import start_rpc_server
from sockets import start_socket
from log import Log
from operation_handler import OperationHandler
from multiprocessing.managers import BaseManager
from multiprocessing import Process
import os

nodes = {
    "148.205.36.206": 5056,
    #"148.205.36.205": 5000
}

def LamportHandlerProxy(log: Log):
    return LamportHandler(nodes, "208", log)

def LogProxy():
    return Log()

def OperationHandlerProxy(log: Log):
    return OperationHandler(log)

def start_server():
    BaseManager.register("LamportHandler", LamportHandlerProxy)
    BaseManager.register("Log", LogProxy)
    BaseManager.register("OperationHandler", OperationHandlerProxy)
    manager = BaseManager(address=("148.205.36.208", 1234))
    manager.start()
    log = manager.Log()
    lamport_handler = manager.LamportHandler(log)
    operation_handler = manager.OperationHandler(log)

    try:
        rpc_server = Process(target=start_rpc_server, args=(lamport_handler, operation_handler))
        socket_process = Process(target=start_socket, args=(lamport_handler,))
        rpc_server.start()
        socket_process.start()
        rpc_server.join()
        socket_process.join()
    except KeyboardInterrupt:
        print('Exiting')
          

if __name__ == '__main__': 
    start_server()
