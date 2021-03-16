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

# https://www.pythonprogramming.in/attribute-assignment-using-getattr-and-setattr-in-python.html
# aplicar __getattr__ and __setattr__ para los managers

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

class MainManager(Manager):
    def __init__(self,context={}):
        self._context=Context(context)
        super(MainManager,self).__init__(self)
        self.iconProvider=None

    @property
    def context(self):
        return self._context
    @context.setter
    def context(self,value):
        self._context=value  

      

    def init(self,plugins=[]):
        
        self.add(TypeManager)
        self.add(EnumManager)
        self.add(ConfigManager)        
        self.add(TaskManager) 
        self.add(ExpManager) 
        self.add(ProcessManager) 
        self.add(TestManager)
        self.add(HelperManager)
        self.add(UiManager)

        for p in plugins:
            self.loadPlugin(p)

    def addIconProvider(self,provider):
        self.iconProvider=provider

    def getIcon(self,_key):
        if self.iconProvider is None: return None
        return self.iconProvider.getIcon(_key) 

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

class ExpManager(Manager):
    def __init__(self,mgr):
        super(ExpManager,self).__init__(mgr)

    def solve(self,exp,context):
        if type(exp) is str: 
            if exp.startswith('$'):
                variable=exp.replace('$','')
                return context[variable]
            elif exp.startswith('enum.'):
                arr=exp.replace('enum.','').split('.')
                return self.mgr.Enum[arr[0]].value(arr[1])
        return exp

    def var(self,exp):
        if type(exp) is str: 
            if exp.startswith('$'):
                return exp.replace('$','')
        return None

    def eval(self,exp,context):
        return True

    def solveParams(self,params,context):  
        for param in params:
            param['value'] = self.solve(param['exp'],context)                    

class TypeManager(Manager):
    def __init__(self,mgr):
        super(TypeManager,self).__init__(mgr)

class Enum():
    def __init__(self,values):
        self.values =values

    def values(self):
        return self.values
    
    def value(self,_key):
        return self.values[_key]

class EnumManager(Manager):
    def __init__(self,mgr):
        super(EnumManager,self).__init__(mgr)

    def applyConfig(self,_key,value):
        self._list[_key]= Enum(value) 

class ConfigManager(Manager):
    def __init__(self,mgr):
        super(ConfigManager,self).__init__(mgr)

    def applyConfig(self,_key,value):
        self._list[_key]= value 

class TaskManager(Manager):
    def __init__(self,mgr):
        super(TaskManager,self).__init__(mgr)

class TestManager(Manager):
    def __init__(self,mgr):
        super(TestManager,self).__init__(mgr)     

class HelperManager(Manager):
    def __init__(self,mgr):
        super(HelperManager,self).__init__(mgr)  

    def add(self,value):
        _key = Helper.rreplace(value.__name__,self.type , '')  
        self._list[_key]= value       

class Process:
    def __init__(self,id,parent,spec,context,mgr):
        self._id=id 
        self._parent=parent
        self._spec=spec
        self._context=Context(context)      
        self.mgr=mgr

    @property
    def id(self):
        return self._id
    @property
    def parent(self):
        return self._parent
    @property
    def spec(self):
        return self._spec        
    @property
    def context(self):
        return self._context

              

    def solveParams(self,params,context):
        return self.mgr.Exp.solveParams(params,context)            

    def node(self,_key):
        return self._spec['nodes'][_key]    

    def start(self):
        self.init()
        starts = dict(filter(lambda p: p[1]['type'] == 'Start', self._spec['nodes'].items()))
        for name in starts:
            start = starts[name]
            if 'exp' in start:
                if self.mgr.Exp.eval(start['exp']):
                    self.execute(name)
            else:
                self.execute(name)        

    def init(self):
        if 'init' in self._spec:
            self.solveParams(self._spec['init'],self._context)
            for p in self._spec['init']:
                print(p)
                self._context[p['name']]=p['value']

    def restart(self):
        pass
        # self.execute(self._context.current)

    def execute(self,_key):
        node=self.node(_key)
        type=node['type'] 
        if type == 'Start':
            self.nextNode(node)
        elif type == 'End':
            self.executeEnd(node)               
        elif type == 'Task':
            self.executeTask(node)
            self.nextNode(node)

        print('executed:'+_key)    
        
    def executeEnd(self,node):
        pass

    def executeTask(self,node):
        try:
            taskManager = self.mgr.Task[node['task']]
            self.solveParams(node['input'],self._context)
            input={}
            for p in node['input']:
                input[p['name']]=p['value'] 
            result=taskManager.execute(**input)
            if 'output' in node:
                for i,p  in enumerate(node['output']):
                    self._context[p['assig']]=result[i] if type(result) is tuple else result   
        except Exception as ex:
            print(ex)
            raise

    def nextNode(self,node):
        if 'transition' not in node: return        
        transition = node['transition']        
        for p in transition:
            if 'exp' in transition:
                if self.mgr.Exp.eval(p['exp']):
                    self.execute(p['target']) 
            else:
                self.execute(p['target'])  
    
import uuid
import threading

class ProcessManager(Manager):
    def __init__(self,mgr):
        self._instances= {}
        super(ProcessManager,self).__init__(mgr)

    
    def create(self,_key,context,parent=None):
        spec=self._list[_key]
        id=str(uuid.uuid4())
        process = Process(id,parent,spec,context,self.mgr)
        self._instances[id]= {"process":process }
        return process

    def start(self,id):        
        try:
            instance = self._instances[id]
            thread = threading.Thread(target=self._process_start, args=(instance["process"],))
            instance["thread"]=thread
            thread.start()
            return instance
        except Exception as ex:
            print(ex)
            raise        

    def _process_start(self,process):
        process.start()

    def getInstance(self,id):
        return self._instances[id]

    def applyConfig(self,_key,value):
        self.completeSpec(_key,value)
        self._list[_key]= value

    def completeSpec(self,_key,spec):
        spec['name']= _key        
        for _key in spec['nodes']:
            self.completeSpecNode(spec['nodes'][_key])
        self.completeSpecVars(spec)
    def completeSpecVars(self,spec):
        vars={}
        if 'input' in spec:
            for p in spec['input']:
                vars[p['name']]={'type':p['type'],'bind':(True if p['name'] in spec['bind'] else False )}  
        if 'nodes' in spec:
            for _key in spec['nodes']:
                node=spec['nodes'][_key]
                if 'input' in node:
                    for p in node['input']:
                        var =self.mgr.Exp.var(p['exp'])
                        if var != None:
                            vars[var]={'type':p['type'],'bind':(True if var in spec['bind'] else False )}  
                if 'output' in node:
                    for p in node['output']:
                        vars[p['assig']]={'type':p['type'],'bind':(True if p['assig'] in spec['bind'] else False )} 
        spec['vars']=vars
    def completeSpecNode(self,node):
        type=node['type'] 
        if type == 'Start':self.completeSpecNodeStart(node)
        elif type == 'End':self.completeSpecNodeEnd(node)            
        elif type == 'Task': self.completeSpecNodeTask(node) 
        return self.completeSpecNodeDefault(node) 
    def completeSpecNodeDefault(self,node):
        self.completeSpecTransition(node)
    def completeSpecNodeStart(self,node):
        self.completeSpecTransition(node)
    def completeSpecNodeEnd(self,node):
        self.completeSpecTransition(node)
    def completeSpecNodeTask(self,node):

        taskSpec=self.mgr.Config['Task'][node['task']]

        if 'input' not in taskSpec: node['input']=[]        
        for p in node['input']:
            p['type'] = next(x for x in taskSpec['input'] if x['name'] == p['name'])['type']
        
        if 'output' not in taskSpec: node['output']=[]        
        for p in node['output']:
            p['type'] = next(x for x in taskSpec['output'] if x['name'] == p['name'])['type']
            
        self.completeSpecTransition(node)        
        return node
    def completeSpecTransition(self,node):        
        if 'transition' not in node:
            node['transition']=[] 
    
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