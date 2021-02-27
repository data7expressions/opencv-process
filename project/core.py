import sys
import yaml
from os import path,getcwd,listdir
import tkinter as tk
import glob
import importlib.util
import inspect

class Helper:
    @staticmethod
    def rreplace(s, old, new, occurrence=1):
        li = s.rsplit(old, occurrence)
        return new.join(li)


class Manager():
    def __init__(self,mgr):
        self.list = {}
        self.mgr=mgr
        self.type = Helper.rreplace(type(self).__name__, 'Manager', '') 

    def add(self,type):
        key = Helper.rreplace(type.__name__,self.type , '')        
        self.list[key]= type(self.mgr)  

    def addConfig(self,key,value):
        self.list[key]= value

    def __getitem__(self,key):
        return self.list[key]  

    def list(self):
        return self.list 

       
    

class MainManager(Manager):
    def __init__(self):
        self._context={}
        super(MainManager,self).__init__(self)

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self,value):
        self._context=value    

    def get(self,type,key):
        return self[type][key] 

    def __getitem__(self,key):
        _key=key
        if _key=='Manager': return self
        return self.list[_key] 

    def add(self,type):
        key = Helper.rreplace(type.__name__,'Manager' , '')        
        self.list[key]= type(self.mgr)

    def applyConfig(self,configPath):
        with open(configPath, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                for type in data:
                    keys=data[type]
                    for key in keys:
                        self[type].addConfig(key,keys[key]) 
            except yaml.YAMLError as exc:
                print(exc)               

    def loadPlugins(self,rootPath):
        files= glob.glob(path.join(rootPath,'**/__plugin__.py'),recursive=True)
        """Load all modules of plugins on rootPath"""
        modules=[]
        pluginsPath=[]
        for file in files:
            pluginPath = path.dirname(file)
            pluginsPath.append(pluginPath)
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
            for key in self.list.keys():
                self.loadTypes(key,module)
        """Load all configurations"""
                  
             
    def loadTypes(self,key,module):
        for element_name in dir(module):
            if element_name.endswith(key) and element_name != key:
                element = getattr(module, element_name)
                if inspect.isclass(element):
                    self[key].add(element) 

class ExpressionManager(Manager):
    def __init__(self,mgr):
        super(ExpressionManager,self).__init__(mgr)

    def solve(self,expresion,context):
        if type(expresion) is str: 
            if expresion.startswith('$'):
                variable=expresion.replace('$','')
                return context['vars'][variable]
            elif expresion.startswith('enum.'):
                arr=expresion.replace('enum.','').split('.')
                return self.mgr.get('Enum',arr[0]).value(arr[1])
                   
        return expresion

    def solveParams(self,params,context):
        result={}    
        for key in params:
            expression = params[key]
            result[key] = self.solve(expression,context) 
        return result                       

class TypeManager(Manager):
    def __init__(self,mgr):
        super(TypeManager,self).__init__(mgr)

class Enum():
    def __init__(self,values):
        self.values =values

    def values(self):
        return self.values
    
    def value(self,key):
        return self.values[key]

class EnumManager(Manager):
    def __init__(self,mgr):
        super(EnumManager,self).__init__(mgr)

    def addConfig(self,key,value):
        self.list[key]= Enum(value) 

class Task():
    def __init__(self,mgr):
        self.mgr=mgr
 
    def setSpec(self,value):
        self.spec=value

    @property
    def input(self):
        return self.spec['input'] 
    @property
    def output(self):
        return self.spec['output']                

class TaskManager(Manager):
    def __init__(self,mgr):
        super(TaskManager,self).__init__(mgr)

    def addConfig(self,key,value):
        self.list[key].setSpec(value)

class TestManager(Manager):
    def __init__(self,mgr):
        super(TestManager,self).__init__(mgr)     

class UiManager(Manager):
    def __init__(self,mgr):
        super(UiManager,self).__init__(mgr)
        self.icons = {}

    def new(self,key,args):
        return self.list[key](*args)

    def init(self):
        self.loadIcons()

    def loadIcons(self):
        iconsPath=path.join(getcwd(),'project/assets/icons')
        for item in listdir(iconsPath):
            name=path.splitext(path.basename(item))[0]
            self.icons[name] = tk.PhotoImage(file=path.join(iconsPath,item))  

    def getIcon(self,key):
        key = key.replace('.','')
        if key not in self.icons: key = '_blank'
        return self.icons[key.replace('.','')]

