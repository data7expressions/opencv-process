from mgr.base import *
from expression.core import Manager as ExpressionManager, Operand
import uuid
import threading

import yaml
from os import path
import glob
import importlib.util
import inspect

# TODO mover a mgr.core
class MainManager(Manager,metaclass=Singleton):
    def __init__(self):
        super(MainManager,self).__init__(self)
    
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

# TODO mover a mgr.core
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

# TODO mover a mgr.core
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

class TaskManager(Manager):
    def __init__(self,mgr):
        super(TaskManager,self).__init__(mgr)

# class ExpManager(Manager):
#     def __init__(self,mgr):
#         super(ExpManager,self).__init__(mgr)
#         self._expManager = ExpressionManager()

#     def addEnum(self,name,values:dict):
#         self._expManager.addEnum(name,values)
#     def getEnum(self,name):
#         return self._expManager.getEnum(name) 

#     def parse(self,string:str)->Operand:
#         return self._expManager.parse(string)
      
#     def eval(self,expression:Operand,context:Context,_type:str=None):
#         result=self._expManager.eval(expression,context)
#         if _type == 'filepath' or _type == 'folderpath' :
#             if not path.isabs(result): 
#                 result = path.join(context['__workspace'], result)        
#         return result

#     # def evalParams(self,params,context):  
#     #     for param in params:
#     #         self.evalParam(param,context)

#     # def evalParam(self,param,context):
#     #     value=None
#     #     if 'exp' in param:
#     #         value = self.solve(param['exp'],context,param['type'])
#     #     elif 'default' in param:
#     #         value = self.solve(param['default'],context,param['type'])  
#     #     param['value'] =value         

class EnumManager(Manager):
    def __init__(self,mgr):
        super(EnumManager,self).__init__(mgr)
        self.expManager = ExpressionManager()

    def applyConfig(self,_key,value):
        self.addEnum(_key,value['values'])

    def addEnum(self,name,values:dict):
        self.expManager.addEnum(name,values)
    def getEnum(self,name):
        return self.expManager.getEnum(name)     



class Process:
    def __init__(self,parent,spec,context,mgr):
        self._id=id 
        self._parent=parent
        self._spec=spec
        self._context=Context(context)      
        self.mgr=mgr
        self.expManager = ExpressionManager()
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

    def eval(self,expression:Operand,context:Context,_type:str=None):
        result=self.expManager.eval(expression,context)
        if _type == 'filepath' or _type == 'folderpath' :
            if not path.isabs(result): 
                result = path.join(context['__workspace'], result)        
        return result

    def node(self,_key):
        return self._spec['nodes'][_key]    

    def init(self):
        if 'input' in self._spec:
            for p in self._spec['input']:
                if p['name'] not in self._context and 'defaultExp' in p:
                    self._context[p['name']] = self.eval(p['defaultExp'],self._context,p['type'])                   

        if 'declare' in self._spec:
            for p in self._spec['declare']:
                if 'defaultExp' in p:
                    self._context[p['name']] = self.eval(p['defaultExp'],self._context,p['type'])
                else:
                    self._context[p['name']] = None      

    def start(self):
        self.context['__status']='running'
        starts = dict(filter(lambda p: p[1]['type'] == 'start', self._spec['nodes'].items()))
        for name in starts:
            start = starts[name]
            if 'expression' in start:
                if self.eval(start['expression'],self._context):
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
            input={}
            for p in node['input']:
                value = self.eval(p['expression'],self._context,p['type'])
                input[p['name']]= value 
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
            if 'expression' in transition:
                if self.eval(p['expression'],self._context):
                    self.execute(p['target']) 
            else:
                self.execute(p['target'])  
   

class ProcessManager(Manager):
    def __init__(self,mgr):
        self._instances= {}
        super(ProcessManager,self).__init__(mgr)
        self.expManager = ExpressionManager()
    
    def create(self,_key:str,context:Context,parent=None):
        spec=self._list[_key]
        return Process(parent,spec,context,self.mgr)

    def apply(self,_key:str,spec:dict,context:Context,parent=None):        
        self.loadSpec(_key,spec)
        self._list[_key]= spec        
        return Process(parent,spec,context,self.mgr)    

    def parse(self,string:str)->Operand:
        return self.expManager.parse(string)    

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
        self.loadSpec(_key,value)
        self._list[_key]= value

    def loadSpec(self,_key,spec:dict):
        spec['name']= _key
        self.loadSpecInit(spec) 
        self.loadSpecDeclare(spec) 
        self.loadSpecVars(spec)        
        for _key in spec['nodes']:
            node=spec['nodes'][_key]
            node['name']=_key
            self.loadSpecNode(node)

    def loadSpecInit(self,spec:dict):
        if 'input' in spec:
            for p in spec['input']:
                if 'default' in p:   
                    p['defaultExp'] = self.parse(p['default'])

    def loadSpecDeclare(self,spec:dict):
        if 'declare' in spec:
            for p in spec['declare']:
                if 'default' in p:   
                    p['defaultExp'] = self.parse(p['default'])                    

    def loadSpecVars(self,spec:dict):
        vars={}
        if 'input' in spec:
            for p in spec['input']:
                var={'type':p['type'],'bind':(True if p['name'] in spec['bind'] else False )}
                vars[p['name']]=var

        if 'declare' in spec:
            for p in spec['declare']:
                var={'type':p['type'],'bind':(True if p['name'] in spec['bind'] else False )}
                vars[p['name']]=var

        spec['vars']=vars
    def loadSpecNode(self,node):
        type=node['type'] 
        if type == 'start':self.loadSpecNodeStart(node)
        elif type == 'end':self.loadSpecNodeEnd(node)            
        elif type == 'task': self.loadSpecNodeTask(node) 
        return self.loadSpecNodeDefault(node) 

    def loadSpecNodeDefault(self,node):
         
        if 'exp' in node:
            node['expression'] = self.parse(node['exp'])
        self.loadSpecTransition(node)

    def loadSpecNodeStart(self,node):
        self.loadSpecTransition(node)
    def loadSpecNodeEnd(self,node):
        self.loadSpecTransition(node)
    def loadSpecNodeTask(self,node):

        taskSpec=self.mgr.Config['Task'][node['task']]

        if 'input' not in taskSpec: node['input']=[]        
        for p in node['input']:
            p['type'] = next(x for x in taskSpec['input'] if x['name'] == p['name'])['type']
            p['expression'] = self.parse(p['exp'])
        
        if 'output' not in taskSpec: node['output']=[]        
        for p in node['output']:
            p['type'] = next(x for x in taskSpec['output'] if x['name'] == p['name'])['type']
            
        self.loadSpecTransition(node)        
        return node
    def loadSpecTransition(self,node):        
        if 'transition' not in node:
            node['transition']=[]
        else:
            for p in node['transition']:
                if 'exp' in p:                
                    p['expression'] = self.parse(p['exp'])    


mainManager = MainManager()
mainManager.add(ConfigManager) 
mainManager.add(TypeManager) 

mainManager.add(EnumManager)
# mainManager.add(ExpManager)     
mainManager.add(TaskManager) 
mainManager.add(ProcessManager) 

dir_path = path.dirname(path.realpath(__file__))
mainManager.loadPlugin(path.join(dir_path,'main'))
