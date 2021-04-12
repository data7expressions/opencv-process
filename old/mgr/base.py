
# # https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
# class Singleton(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]

# # https://www.geeksforgeeks.org/mimicking-events-python/
# class Event(object): 
  
#     def __init__(self): 
#         self.__handlers = [] 
  
#     def __iadd__(self, handler): 
#         self.__handlers.append(handler) 
#         return self
  
#     def __isub__(self, handler): 
#         self.__handlers.remove(handler) 
#         return self
  
#     def __call__(self, *args, **keywargs): 
#         for handler in self.__handlers: 
#             handler(*args, **keywargs) 

# class Mediator():
#     def __init__(self):
#         self._onMessage=Event()

#     @property
#     def onMessage(self):
#         return self._onMessage

#     @onMessage.setter
#     def onMessage(self,value):
#         self._onMessage=value           

#     def send(self,sender,verb,resource=None,args={}):
#         self._onMessage(sender,verb,resource,args)

# # https://www.semicolonworld.com/question/43363/how-to-ldquo-perfectly-rdquo-override-a-dict
# class Context(dict):
#     def __init__(self, data={}):
#         super(Context, self).__init__(data)
#         self._onChange=Event()

#     @property
#     def onChange(self):
#         return self._onChange
#     @onChange.setter
#     def onChange(self,value):
#         self._onChange=value     
    
#     def __setitem__(self, key, value):
#         oldValue = self[key] if key in self else None        
#         super(Context, self).__setitem__(key, value)
#         self._onChange(key,value,oldValue)   

# class Helper:
#     @staticmethod
#     def rreplace(s, old, new, occurrence=1):
#         li = s.rsplit(old, occurrence)
#         return new.join(li)

#     @staticmethod
#     def nvl(value, default):
#         if value is None:
#             return default
#         return value  

# class Manager():
#     def __init__(self,mgr):
#         self._list = {}
#         self.mgr=mgr
#         self.type = Helper.rreplace(type(self).__name__, 'Manager', '') 

#     def __getattr__(self, _key):
#         if _key in self._list: return self._list[_key]
#         else: return None
#     def __getitem__(self,_key):
#         return self._list[_key]        
#     @property
#     def list(self):
#         return self._list

#     def add(self,value):
#         _key = Helper.rreplace(value.__name__,self.type , '')  
#         self._list[_key]= value(self.mgr)

#     def applyConfig(self,_key,value):
#         self._list[_key]= value    

#     def key(self,value):
#         if type(value).__name__ != 'type':
#             return  Helper.rreplace(type(value).__name__,self.type , '')
#         else:
#             return  Helper.rreplace(value.__name__,self.type , '')  