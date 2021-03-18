# https://www.geeksforgeeks.org/mimicking-events-python/
class Event(object): 
  
    def __init__(self): 
        self.__handlers = [] 
  
    def __iadd__(self, handler): 
        self.__handlers.append(handler) 
        return self
  
    def __isub__(self, handler): 
        self.__handlers.remove(handler) 
        return self
  
    def __call__(self, *args, **keywargs): 
        for handler in self.__handlers: 
            handler(*args, **keywargs) 

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


# https://www.semicolonworld.com/question/43363/how-to-ldquo-perfectly-rdquo-override-a-dict
class Context(dict):
    def __init__(self, data={}):
        super(Context, self).__init__(data)
        self._onChange=Event()

    @property
    def onChange(self):
        return self._onChange
    @onChange.setter
    def onChange(self,value):
        self._onChange=value     
    
    def __setitem__(self, key, value):
        oldValue = self[key] if key in self else None        
        super(Context, self).__setitem__(key, value)
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


class Point(object):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,value):
        self._x=value
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,value):
        self._y=value           

    def move(self, dx, dy):
        self._x = self._x + dx
        self._y = self._y + dy

    def __str__(self):
        return "Point(%s,%s)"%(self._x, self._y) 

class Size(object):
    def __init__(self, w, h):
        self._w = w
        self._h = h

    @property
    def w(self):
        return self._w
    @w.setter
    def w(self,value):
        self._w=value
    @property
    def h(self):
        return self._h
    @h.setter
    def h(self,value):
        self._h=value           

    def move(self, dw, dh):
        self._w = self._w + dw
        self._h = self._h + dh

    def __str__(self):
        return "Point(%s,%s)"%(self._w, self._y) 

    