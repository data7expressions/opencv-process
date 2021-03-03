import yaml
from os import path
import glob
import importlib.util
import inspect
import sys
from enum import Enum
import tkinter as tk
from os import path,listdir
from .base import *



class Manager():
    def __init__(self,mgr):
        self.list = {}
        self.mgr=mgr
        self.type = Helper.rreplace(type(self).__name__, 'Manager', '') 

    def add(self,value):
        key = Helper.rreplace(value.__name__,self.type , '')  
        self.list[key]= value(self.mgr)

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
        self.iconProvider=None

    def init(self,plugins=[]):
        
        self.add(TypeManager)
        self.add(EnumManager)
        self.add(ConfigManager)        
        self.add(TaskManager) 
        self.add(ExpressionManager) 
        self.add(ProcessManager) 
        self.add(TestManager)
        self.add(HelperManager)
        self.add(UiManager)

        for p in plugins:
            self.loadPlugin(p)

    def addIconProvider(self,provider):
        self.iconProvider=provider

    def getIcon(self,key):
        if self.iconProvider is None: return None
        return self.iconProvider.getIcon(key) 

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self,value):
        self._context=value    
    
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
            for key in self.list.keys():
                self.loadTypes(key,module)
        """Load all configurations"""        
        list = glob.glob(path.join(pluginPath,'**/*.y*ml'),recursive=True)
        for item in list:
            self.applyConfig(path.join(pluginPath,item))                  
            
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
                return self.mgr['Enum'][arr[0]].value(arr[1])
                   
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

class ConfigManager(Manager):
    def __init__(self,mgr):
        super(ConfigManager,self).__init__(mgr)

    def addConfig(self,key,value):
        self.list[key]= value 

class TaskManager(Manager):
    def __init__(self,mgr):
        super(TaskManager,self).__init__(mgr)

    def addConfig(self,key,value):
        self.list[key].setSpec(value)

class TestManager(Manager):
    def __init__(self,mgr):
        super(TestManager,self).__init__(mgr)     

class HelperManager(Manager):
    def __init__(self,mgr):
        super(HelperManager,self).__init__(mgr)  

    def add(self,value):
        key = Helper.rreplace(value.__name__,self.type , '')  
        self.list[key]= value       

class Process:
    def __init__(self,mgr,parent,spec,context):        
        self.mgr=mgr
        self.parent=parent
        self.spec=spec
        self.context=context 

    def solveParams(self,params,context):
        return self.mgr['Expression'].solveParams(params,context)            

    def node(self,key):
        return self.spec['nodes'][key]    

    def start(self):
        self.init()
        self.execute('start')

    def init(self):
        if 'init' in self.spec:
            vars = self.solveParams(self.spec['init'],self.context)
            for k in vars:
                self.context['vars'][k]=vars[k] 

    def restart(self):
        self.execute(self.context.current)

    def execute(self,key):
        node=self.node(key)
        type=node['type'] 
        if type == 'Start':
            self.nextNode(node)
        elif type == 'End':
            self.executeEnd(node)               
        elif type == 'Task':
            self.executeTask(node)
            self.nextNode(node)
        
    def executeEnd(self,node):
        print('End')

    def executeTask(self,node):
        try:
            taskManager = self.mgr['Task'][node['task']]
            input = self.solveParams(node['input'],self.context)
            result=taskManager.execute(**input)
            if 'output' in node:
                self.context['vars'][node['output']]=result  
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def nextNode(self,node):
        if 'transition' not in node: return        
        transition = node['transition']        
        if type(transition) is str:self.execute(transition) 
        elif type(transition) is list: 
            for p in transition:self.execute(p) 
        elif type(transition) is dict: 
            for k in transition:self.execute(transition[k])
    
class ProcessManager(Manager):
    def __init__(self,mgr):
        self._instances= []
        super(ProcessManager,self).__init__(mgr)    

    def start(self,key,context):
        spec=self.list[key]
        instance=Process(self.mgr,self,spec,context)
        self._instances.append(instance)
        instance.start()
    
class UiManager(Manager):
    def __init__(self,mgr):
        super(UiManager,self).__init__(mgr)

    def add(self,value):
        key = Helper.rreplace(value.__name__,self.type , '')  
        self.list[key]= value     

    def singleton(self,key,args={}):
        value=self.list[key]
        if type(value).__name__ != 'type':
            return value

        args['mgr']=self.mgr
        instance=value(**args)
        self.list[key]= instance
        return instance

    def new(self,key,args={}):
        value=self.list[key]
        _class=None
        if type(value).__name__ == 'type':
            _class=value
        else:
            _class=type(value)
        args['mgr']=self.mgr
        return _class(**args) 