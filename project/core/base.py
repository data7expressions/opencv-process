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