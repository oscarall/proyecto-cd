import socket
import json

class LamportHandler:

    def __init__(self, nodes, id):
        self.nodes = [Node(ip, port) for ip, port in nodes.items()]
        self.requests = []
        self.id = id
        self.reply_table = {}
        self.reset_reply_table()
        self.values = {
            "x": 0,
            "y": 0
        }
        self.time = 0
        
    def reset_reply_table(self):
        for node in self.nodes:
            node_id = node.ip.split('.')[3]
            self.reply_table[node_id] = 0

    def request_mutual_exclusion(self, req):
        self.increment_timer()
        req["time"] = self.time
        req["sender"] = self.id
        self.requests.append(req)
        print(self.requests)
        self.broadcast(req)

    def broadcast(self, msg):
        for node in self.nodes:
            node.send_message(json.dumps(msg))

    def external_request(self, req):
        time = int(req.get("time"))
        self.time = max(time, self.time) + 1
        id = req["sender"]
        node = self.get_node(id)
        
        if not node:
            print(f"Invalid node {id}")
        
        self.requests.append(req)
        msg = {"reply":"reply", "id": self.id, "time": self.time}
        node.send_message(json.dumps(msg))


    def get_node(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
        
        return None

    def reply(self, id):
        self.reply_table[id] = 1
        print(self.reply_table)
        self.check_critic_section()
    
    def check_critic_section(self):
        for id, reply in self.reply_table.items():
            if reply == 0:
                return
        
        if self.requests[0]["sender"] == self.id:
            self.critic_section()
            self.release()

    def critic_section(self):
        print("In the critic section")
        request = self.requests.pop(0)
        action = request["action"].upper()
        value = int(request["value"])
        target = request["target"]

        print(f"Applying {action} to {target} value {value}")

        if (action == "ADD"):
            response = self.add(target, value)
        elif (action == "MULTIPLY"):
            response = self.multiply(target, value)


    def release_request(self, release):
        print("Got release")
        id = release["id"]

        if id == self.requests[0]["sender"]:
            self.critic_section()
        
        self.check_critic_section()
    
    def release(self):
        msg = {"release":"release", "id": self.id, "time": self.time}
        self.broadcast(msg)
        self.reset_reply_table()

    def increment_timer(self):
        self.time += 1

    def add(self, target, value):
        self.values[target.lower()] = self.values[target.lower()] + value

    def multiply(self, target, value):
        self.values[target.lower()] = self.values[target.lower()] * value
    
    def get(self, target):
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
