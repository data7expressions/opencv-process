
class Manager:
    main:None
    def __init__(self):
        self.list = {}

    def add(self,value):
        value.main = self
        key=type(value).__name__
        self.list[key]= value    

    def addConfig(self,key,value):
        self.list[key]= value

    def el(self,key):
        return self.list[key]    

    def loadConfig(self,value):
        for key in value:
            self.addConfig(key,value[key])




