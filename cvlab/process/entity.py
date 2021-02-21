class EnumEntity():
    def __init__(self,values):
        self._values =values

    @property
    def values(self):
        return self._values

class FunctionEntity:
    def __init__(self,definition=None):
        self._definition=definition

    @property    
    def definition(self):
        return self._definition        

    @definition.setter    
    def definition(self,value):
        self._definition=value

    @property    
    def description(self):
        return self._definition['description'] 

    @property    
    def parameters(self):
        return self._definition['parameters'] 

    @property    
    def output(self):
        return self._definition['output']   