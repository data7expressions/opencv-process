# https://www.geeksforgeeks.org/mimicking-events-python/
class Event(object): 
  
    def __init__(self): 
        self.__eventhandlers = [] 
  
    def __iadd__(self, handler): 
        self.__eventhandlers.append(handler) 
        return self
  
    def __isub__(self, handler): 
        self.__eventhandlers.remove(handler) 
        return self
  
    def __call__(self, *args, **keywargs): 
        for eventhandler in self.__eventhandlers: 
            eventhandler(*args, **keywargs) 

class Mediator():
    def __init__(self):
        self._onMessage=Event()

    @property
    def onMessage(self):
        return self._onMessage

    @onMessage.setter
    def onMessage(self,value):
        self._onMessage=value           

    def send(self,sender,verb,resource=None,args={}):
        self._onMessage(sender,verb,resource,args)

class Context:
    def __init__(self,vars={}):
        self._vars=vars 
        self._onChange=Event()

    @property
    def onChange(self):
        return self._onChange
    @onChange.setter
    def onChange(self,value):
        self._onChange=value  

    def get(self,key):
        return self._vars[key]
    def set(self,key,value):
        oldValue = self._vars[key]
        if oldValue != value:
            self._vars['key']=value
            self._onChange(key,value,oldValue)

class Helper:
    @staticmethod
    def rreplace(s, old, new, occurrence=1):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    @staticmethod
    def nvl(value, default):
        if value is None:
            return default
        return value    