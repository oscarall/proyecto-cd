import socket
import json

class LamportHandler:

    def __init__(self, nodes, id, action_handler):
        self.nodes = [Node(ip, port) for ip, port in nodes.items()]
        self.requests = []
        self.id = id
        self.reply_table = {}
        self.reset_reply_table()
        self.values = {
            "x": 0
            "y": 0
        }
        self.time = 0
        
    def reset_reply_table(self):
        for node in self.nodes:
            node_id = node.ip.split('.')[3]
            reply_table[node_id] = 0

    def request_mutual_exclusion(self, req):
        req["sender"] = self.id
        self.requests.append(req)
        self.broadcast(request)

    def broadcast(self, msg):
        for node in self.nodes:
            node.send_message(self, json.dumps(msg))

    def external_request(self, req):
        id = req["sender"]
        node = get_node(id)
        
        if not node:
            print(f"Invalid node {id}")
        
        self.requests.append(req)
        msg = {"reply":"reply", "id": self.id}
        node.send_message(json.dumps(msg))


    def get_node(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
        
        return None

    def reply(self, ip):
        id = ip.split('.')[3]
        self.reply_table[id] = 1
        self.check_critic_section()
    
    def check_critic_section(self):
        for id, reply in self.reply_table:
            if reply == 0:
                return
        
        if requests[0]["id"] == self.id:
            critic_section()

    def critic_section(self):
        request = requests.pop(0)
        action = request["action"].upper()
        value = int(request["value"])
        target = request["target"]

        if (action == "ADD"):
            response = self.action_handler.add_value(value, target)
        elif (action == "MULTIPLY"):
            response = self.action_handler.multiply_value(value, target)

    def release_request(self, release):
        id = release["id"]

        if id == self.requests[0]["sender"]:
            self.critic_section()
        
        self.check_critic_section()
    
    def release(self):
        msg = {"release":"release", "id": self.id}
        self.broadcast(json.dumps(msg))
        self.reset_reply_table()

    def increment_timer(self):
        self.time += 1

    def add(self, target, value):
        self.increment_timer()
        self.values[target.lower()] = self.values[target.lower()] + value

    def multiply(self, target, value):
        self.increment_timer()
        self.values[target.lower()] = self.values[target.lower()] * value
    
    def get(self, target)
        self.increment_timer()
        return self.values[target.lower()]

class Node:
    def __init__(self, ip, port):
        self.id = ip.split('.')[3]
        self.ip = ip
        self.port = port
    
    def send_message(self, msg):
        print(f"Sending message to {self.id} -> {msg}")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.ip, self.port))
        client.send((msg+'\n').encode('utf-8'))
        client.close()
