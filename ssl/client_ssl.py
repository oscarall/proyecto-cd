
import os
import xmlrpc.client
import ssl
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.environ.get('PASSWORD')
SERVER_HOST = os.getenv("SERVER_HOST", 'localhost')
url = f'https://{USER}:{PASSWORD}@{SERVER_HOST}:443'
try:
    #    Connects to server
    #    Can only connect over HTTPS with HTTPS server
    #    Server supports passing username and password
    s = xmlrpc.client.ServerProxy(url, context=ssl._create_unverified_context())
    student = s.get_student(3)
    print(student)
except Exception as e:
    print(e)



