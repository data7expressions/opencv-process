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
        
        dir_path = path.dirname(path.realpath(__file__))
        self.loadPlugin(path.join(dir_path,'main'))

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

# class Enum():
#     def __init__(self,values):
#         self.values =values
#     def values(self):
#         return self.values    
#     def value(self,_key):
#         return self.values[_key]

from expression.core import Manager as ExpressionManager

class ExpManager(Manager):
    def __init__(self,mgr):
        super(ExpManager,self).__init__(mgr)
        self._expManager = ExpressionManager()

    def addEnum(self,name,values:dict):
        self._expManager.addEnum(name,values)
    def getEnum(self,name):
        return self._expManager.getEnum(name)    

    def solve(self,exp,_type,context):
        if type(exp) is str: 
            if exp.startswith('$'):
                variable=exp.replace('$','')
                return context[variable]
            elif exp.startswith('enum.'):
                arr=exp.replace('enum.','').split('.')
                return self.mgr.Enum[arr[0]].value(arr[1])
        elif type(exp) is dict:
            return exp        

        if _type == 'filepath' or _type == 'folderpath' :
            if not path.isabs(exp): 
                exp = path.join(context['__workspace'], exp)        
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
            self.solveParam(param,context)

    def solveParam(self,param,context):
        value=None
        if 'exp' in param:
            value = self.solve(param['exp'],param['type'],context)
        elif 'default' in param:
            value = self.solve(param['default'],param['type'],context)  
        param['value'] =value         

class EnumManager(Manager):
    def __init__(self,mgr):
        super(EnumManager,self).__init__(mgr)

    def applyConfig(self,_key,value):
        self.mgr.Exp.addEnum(_key,value['values'])
        # self._list[_key]= Enum(value['values']) 

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
    def __init__(self,parent,spec,context,mgr):
        self._id=id 
        self._parent=parent
        self._spec=spec
        self._context=Context(context)      
        self.mgr=mgr
        self.init()

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self,value):
        self._id=value      
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

    def init(self):
        if 'input' in self._spec:
            self.solveParams(self._spec['input'],self._context)
            for p in self._spec['input']:
                self._context[p['name']]=p['value']

        if 'init' in self._spec:
            self.solveParams(self._spec['init'],self._context)
            for p in self._spec['init']:
                self._context[p['name']]=p['value']

    def start(self):
        self.context['__status']='running'
        starts = dict(filter(lambda p: p[1]['type'] == 'start', self._spec['nodes'].items()))
        for name in starts:
            start = starts[name]
            if 'exp' in start:
                if self.mgr.Exp.eval(start['exp']):
                    self.execute(name)
            else:
                self.execute(name)        

    def stop(self):
        self._context['__status']='stopping'
    def pause(self):
        self._context['__status']='pausing'   

    def execute(self,_key):
        if self._context['__status']=='running':            
            node=self.node(_key)
            self._context['__current']=node 
            type=node['type'] 
            if type == 'start':
                self.executeStart(node)
            elif type == 'task':
                self.executeTask(node)    
            elif type == 'end':
                self.executeEnd(node)            

            self._context['__last']=node  
            self.nextNode(node)
        elif self._context['__status']=='pausing':
            self._context['__status']='paused'   
        elif self._context['__status']=='stopping':
            self._context['__status']='stopped'              

    def executeStart(self,node):
        pass    
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
    
    def create(self,_key:str,context:Context,parent=None):
        spec=self._list[_key]
        return Process(parent,spec,context,self.mgr)

    def apply(self,_key:str,spec:dict,context:Context,parent=None):        
        self.completeSpec(_key,spec)
        self._list[_key]= spec        
        return Process(parent,spec,context,self.mgr)    

    def start(self,process:Process):        
        try:
            process.id = str(uuid.uuid4())             
            thread = threading.Thread(target=self._process_start, args=(process,))
            self._instances[process.id]= {"process":process,"thread":thread }            
            thread.start()
            return process.id
        except Exception as ex:
            print(ex)
            raise

    def stop(self,id):
        self._instances[id]['process'].stop() 

    def pause(self,id):
        self._instances[id]['process'].pause()     


    def _process_start(self,process):
        process.start()

    def getInstance(self,id):
        return self._instances[id]

    def applyConfig(self,_key,value):
        self.completeSpec(_key,value)
        self._list[_key]= value

    def completeSpec(self,_key,spec:dict):
        spec['name']= _key        
        for _key in spec['nodes']:
            node=spec['nodes'][_key]
            node['name']=_key
            self.completeSpecNode(node)
        self.completeSpecVars(spec)
    def completeSpecVars(self,spec:dict):
        vars={}
        if 'input' in spec:
            for p in spec['input']:
                var={'type':p['type'],'bind':(True if p['name'] in spec['bind'] else False )}  
                if 'default' in p : var['default'] = p['default']
                vars[p['name']]=var 
        if 'nodes' in spec:
            for _key in spec['nodes']:
                node=spec['nodes'][_key]
                if 'input' in node:
                    for p in node['input']:
                        varName =self.mgr.Exp.var(p['exp'])
                        if varName != None:
                            var={'type':p['type'],'bind':(True if varName in spec['bind'] else False )}
                            if 'default' in p : var['default'] = p['default']
                            vars[varName]=var   
                if 'output' in node:
                    for p in node['output']:
                        vars[p['assig']]={'type':p['type'],'bind':(True if p['assig'] in spec['bind'] else False )}

        for name in vars:
            vars[name]['isInput']= len(list(filter (lambda p : p['name'] == name, spec['input']))) > 0

        if 'init' in spec:
            for p in spec['init']:
                if p['name'] in vars:
                    var = vars[p['name']]
                    p['type']=var['type']



        spec['vars']=vars
    def completeSpecNode(self,node):
        type=node['type'] 
        if type == 'start':self.completeSpecNodeStart(node)
        elif type == 'end':self.completeSpecNodeEnd(node)            
        elif type == 'task': self.completeSpecNodeTask(node) 
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
