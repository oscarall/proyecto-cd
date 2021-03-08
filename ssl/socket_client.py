import socket
import json

msg = {
    "reply": "reply",
    "id": "203"
}

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("148.205.36.208", 3000))
client.send((json.dumps(msg)+'\n').encode('utf-8'))
client.close()