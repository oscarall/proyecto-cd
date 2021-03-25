from log import Log

class OperationHandler:

    def __init__(self, log: Log):
        self.values = {
            "x": 0,
            "y": 0
        }
        self.log = log
        self.log.suscribe(self)
        self.pointer = 0

    def get_name(self):
        return "Operation handler"
    
    def notify(self):
        item = self.log.read(self.pointer)
        
        if item == {}:
            return
        
        self.pointer += 1
        self.apply(item)

        
    def apply(self, item):
        action = item["action"].upper()
        value = int(item["value"])
        target = item["target"]

        print(f"Applying {action} to {target} value {value}")

        if (action == "ADD"):
            self.add(target, value)
        elif (action == "MULTIPLY"):
            self.multiply(target, value)

    def add(self, target, value):
        self.values[target.lower()] = self.values[target.lower()] + value

    def multiply(self, target, value):
        self.values[target.lower()] = self.values[target.lower()] * value
    
    def get(self, target):
        return self.values[target.lower()]
