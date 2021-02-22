
class Manager:
    main:None
    def __init__(self,main=None,parent=None):
        self.list = {}
        self._main=main
        self._parent=parent

    @property    
    def main(self):
        return self._main
    @main.setter    
    def main(self,value):
        self._main=value
    @property    
    def parent(self):
        return self._parent
    @parent.setter    
    def parent(self,value):
        self._parent=value    


    def add(self,value):
        value.main = self._main
        value.parent = self
        key=type(value).__name__
        self.list[key]= value    

    def addConfig(self,key,value):
        self.list[key]= value

    def get(self,key):
        return self.list[key]    

    def loadConfig(self,value):
        for key in value:
            self.addConfig(key,value[key])

    
    

