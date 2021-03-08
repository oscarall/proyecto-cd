from lamport import LamportHandler
from rpc import start_rpc_server
from socket import start_socket
from multiprocessing.managers import BaseManager

def start_server(): 
    BaseManager.register('LamportHandler', LamportHandler)
    manager = BaseManager()
    manager.start()
    lamport_handler = manager.LamportHandler()


    n = os.fork() 
    try:
        if n > 0: 
            print("Parent process and id is : ", os.getpid())
            start_rpc_server() 
        else:
            print("Child process and id is : ", os.getpid())
            start_socket()
    except KeyboardInterrupt:
        print('Exiting')
          

if __name__ == '__main__': 
    start_server()
