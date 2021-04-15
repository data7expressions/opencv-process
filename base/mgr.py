import yaml
from os import path
import glob
import importlib.util
import inspect

# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

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

class Manager():
    def __init__(self,mgr):
        self._list = {}
        self.mgr=mgr
        self.type = Helper.rreplace(type(self).__name__, 'Manager', '') 

    def __getattr__(self, _key):
        if _key in self._list: return self._list[_key]
        else: return None
    def __getitem__(self,_key):
        return self._list[_key]        
    @property
    def list(self):
        return self._list

    def add(self,value):
        _key = Helper.rreplace(value.__name__,self.type , '')  
        self._list[_key]= value(self.mgr)

    def applyConfig(self,_key,value):
        self._list[_key]= value    

    def key(self,value):
        if type(value).__name__ != 'type':
            return  Helper.rreplace(type(value).__name__,self.type , '')
        else:
            return  Helper.rreplace(value.__name__,self.type , '')  

class IconProvider():
    def __init__(self,iconsPath=None): 
        self.icons = {}
        if iconsPath is not None:
           self.loadIcons(iconsPath)

    def loadIcons(self,iconsPath):
        pass

    def getIcon(self,key):
        key = key.replace('.','')
        if key not in self.icons: key = '_blank'
        return self.icons[key.replace('.','')] 

class MainManager(Manager,metaclass=Singleton):
    def __init__(self):
        super(MainManager,self).__init__(self)
        self.iconProvider = None
        self.init()

    def init(self):
            
        self.add(TypeManager)
        self.add(ConfigManager)        
        self.add(UiManager)  

        dir_path = path.dirname(path.realpath(__file__))
        self.loadPlugin(path.join(dir_path,'main'))   
    
    def __getattr__(self, _key):
        if _key=='Manager': return self      
        if _key in self._list: return self._list[_key]
        else: return None
    def __getitem__(self,_key):
        if _key=='Manager': return self
        return self._list[_key] 

    def add(self,type):
        _key = Helper.rreplace(type.__name__,'Manager' , '')        
        self._list[_key]= type(self.mgr)

    def applyConfig(self,configPath):
        with open(configPath, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                for type in data:
                    _keys=data[type]
                    for _key in _keys:
                        self[type].applyConfig(_key,_keys[_key]) 
            except yaml.YAMLError as exc:
                print(exc)
            except Exception as ex:
                print(ex)                   

    def loadPlugin(self,pluginPath):
        
        """Load all modules of plugins on pluginPath"""
        modules=[]
        list = glob.glob(path.join(pluginPath,'**/*.py'),recursive=True)
        for item in list:
            modulePath= path.join(pluginPath,item)
            file= path.basename(item)
            filename, fileExtension = path.splitext(file)
            if not filename.startswith('_'):
                name = modulePath.replace('/','_')   
                spec = importlib.util.spec_from_file_location(name, modulePath)   
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                modules.append(module)
        """Load all managers on modules loaded"""
        for module in modules:
            self.loadTypes('Manager',module)
        """Load others types on modules loaded"""
        for module in modules:
            for _key in self._list.keys():
                self.loadTypes(_key,module)
        """Load all configurations"""        
        list = glob.glob(path.join(pluginPath,'**/*.y*ml'),recursive=True)
        for item in list:
            self.applyConfig(path.join(pluginPath,item))                  
            
    def loadTypes(self,_key,module):
        for element_name in dir(module):
            if element_name.endswith(_key) and element_name != _key:
                element = getattr(module, element_name)
                if inspect.isclass(element):
                    self[_key].add(element)

    def addIconProvider(self,iconProvider:IconProvider):
        self.iconProvider =iconProvider                     

    def getIcon(self,key):
       return self.iconProvider.getIcon(key) if self.iconProvider != None else None

class ConfigManager(Manager):
    def __init__(self,mgr):
        super(ConfigManager,self).__init__(mgr)

    def applyConfig(self,_key,value):
        if _key in self._list:
            config = self._list[_key]
            for p in value:
                config[p]=value[p]
        else:
            self._list[_key]= value 

class TypeManager(Manager):
    def __init__(self,mgr):
        super(TypeManager,self).__init__(mgr)

    def range(self,type):
        from_=None
        to= None
        if type['sign'] ==  True:
            to = (type['precision'] * 16)
            from_ = (to-1)*-1 
        else:
            to = type['precision'] * 32
            from_ = 0 
        return from_,to          
   
class UiManager(Manager):
    def __init__(self,mgr):
        super(UiManager,self).__init__(mgr)

    def add(self,value):
        _key = Helper.rreplace(value.__name__,self.type , '')  
        self._list[_key]= value 

    def singleton(self,_key,**args):
        value=self._list[_key]
        if type(value).__name__ != 'type':
            return value

        args['mgr']=self.mgr
        instance=value(**args)
        self._list[_key]= instance
        return instance

    def new(self,_key,**args):
        value=self._list[_key]
        _class=None
        if type(value).__name__ == 'type':
            _class=value
        else:
            _class=type(value)
        args['mgr']=self.mgr
        return _class(**args) 
