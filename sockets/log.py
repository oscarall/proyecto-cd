class Log:
    def __init__(self):
        self.log_data = []
        self.suscriptors = []
    
    def suscribe(self, suscriptor):
        print(f"Subscribing {suscriptor.get_name()}")
        self.suscriptors.append(suscriptor)
    
    def read(self, pointer: int):
        if pointer >= len(self.log_data):
            return {}
        return self.log_data[pointer]
    
    def write(self, item):
        self.log_data.append(item)
        self.notify()

    def notify(self):
        for suscriptor in self.suscriptors:
            suscriptor.notify()