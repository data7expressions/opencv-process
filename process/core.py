from mgr.base import *
from expression.core import Manager as ExpressionManager, Operand
import uuid
import threading

import yaml
from os import path
import glob
import importlib.util
import inspect
from multiprocessing import Process as ParallelProcess

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




class ProcessError(Exception):pass

class Object(object):pass

class ProcessSpec(object):pass

class BpmParser:
    def __init__(self,mgr,expManager):
        self.mgr = mgr
        self.expManager = expManager     

    def parse(self,spec:dict)-> ProcessSpec:
        process = ProcessSpec()
        process.name= spec['name']
        process.type= spec['type']
        process.bind = spec['bind'] if 'bind' in spec else []
        process.input=self.parseInput(spec) 
        process.declare=self.parseDeclare(spec) 
        process.vars=self.getVars(process)
        process.nodes = {}        
        for key in spec['nodes']:
            specNode=spec['nodes'][key]
            specNode['name']=key
            process.nodes[key] =self.parseNode(specNode)
        return process    

    def parseInput(self,spec:dict):
        input = []
        if 'input' in spec:
            for p in spec['input']:
                param  = Object()
                param.name = p['name']
                param.type = p['type']
                param.default = self.expManager.parse(p['default']) if 'default' in p else None
                input.append(param)
        return input         

    def parseDeclare(self,spec:dict):
        declare = []
        if 'declare' in spec:
            for p in spec['declare']:
                param  = Object()
                param.name = p['name']
                param.type = p['type']
                param.default = self.expManager.parse(p['default']) if 'default' in p else None
                declare.append(param)
        return declare                            

    def getVars(self,process:ProcessSpec):
        vars={}    
        for p in process.input:
            var = Object
            var.type=p.type
            var.bind = True if p.name in process.bind else False
            vars[p.name]=var        
        for p in process.declare:
            var = Object
            var.type=p.type
            var.bind = True if p.name in process.bind else False
            vars[p.name]=var
        return vars
    
    def parseNode(self,spec):
        type=spec['type'] 
        if type == 'start':return self.parseNodeStart(spec)
        elif type == 'end':return self.parseNodeDefault(Object(),spec)           
        elif type == 'task':return self.parseNodeTask(spec)
        elif type == 'exclusiveGateway':return self.parseNodeGateway(spec)
        elif type == 'inclusiveGateway':return self.parseNodeGateway(spec)
        elif type == 'parallelGateway':return self.parseNodeGateway(spec)
        else: raise ProcessError('not found node type :'+type) 
     
    def parseNodeStart(self,spec):        
        node= self.parseNodeDefault(Object(),spec)
        node.expression = self.expManager.parse(spec['exp']) if 'exp' in spec else None
        return node
    def parseNodeTask(self,spec):        
        node= self.parseNodeDefault(Object(),spec)
        node.task = Object()
        node.task.name= spec['task']
        node.task.input= []
        node.task.output= []
        taskSpec=self.mgr.Config['Task'][spec['task']]
        if 'input' in taskSpec:       
            for p in spec['input']:
                param = Object()
                param.name = p['name']
                param.type = next(x for x in taskSpec['input'] if x['name'] == p['name'])['type']
                param.expression = self.expManager.parse(p['exp'])
                node.task.input.append(param)
        if 'output' in taskSpec:   
            for p in spec['output']:
                param = Object()
                param.name = p['name']
                param.type = next(x for x in taskSpec['output'] if x['name'] == p['name'])['type']
                param.assig = p['assig']                
                node.task.output.append(param)        
        return node

    def parseNodeGateway(self,spec):        
        node= self.parseNodeDefault(Object(),spec)
        node.key = spec['key'] if 'key' in spec else 'default'
        return node
    # TODO
    def parseNodeScript(self,spec):pass
    # TODO
    def parseNodeEventGateway(self,spec):pass
    # TODO
    def parseNodeSubProcess(self,spec):pass
    # TODO
    def parseNodeUserTask(self,spec):pass
    # TODO
    def parseNodeServiceTask(self,spec):pass
    # TODO
    def parseNodeEventSignal(self,spec):pass
    # TODO
    def parseNodeStartSignal(self,spec):pass
    # TODO
    def parseNodeRaiseSignal(self,spec):pass

    def parseNodeDefault(self,node,spec):
        node.name = spec['name']
        node.type = spec['type']
        node.transition = self.parseTransition(spec)
        return node

    def parseTransition(self,spec):
        transition = []
        if 'transition' in spec:
            for p in spec['transition']:
                item = Object()
                item.target = p['target']
                item.expression = self.expManager.parse(p['exp']) if 'exp' in p else None
                transition.append(item)
        return transition        

class ProcessInstance:
    def __init__(self,parent:str,spec:ProcessSpec,context:Context,mgr:MainManager,expManager:ExpressionManager):
        self._id=None 
        self._parent=parent
        self._context=context
        self._spec=spec      
        self.mgr=mgr
        self.expManager = expManager 
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

    def init(self):
        for p in self._spec.input:
            if p.name not in self._context and p.default != None:
                self._context[p.name] = self.eval(p.default,self._context,p.type)        
        for p in self._spec.declare:
            self._context[p.name] = self.eval(p.default,self._context,p.type) if p.default != None else None    

    def eval(self,expression:Operand,context:Context,_type:str=None):
        result=self.expManager.eval(expression,context)
        if _type == 'filepath' or _type == 'folderpath' :
            if not path.isabs(result): 
                result = path.join(context['__workspace'], result)        
        return result 

class BpmInstance(ProcessInstance):
    def __init__(self,parent:str,spec:ProcessSpec,context:Context,mgr:MainManager,expManager:ExpressionManager):
        super(BpmInstance,self).__init__(parent,spec,context,mgr,expManager)
        self.gateways= {}

    def start(self):
        self.context['__status']='running'
        starts = dict(filter(lambda p: p[1].type == 'start', self._spec.nodes.items()))
        for name in starts:
            p = starts[name]
            if p.expression != None:
                if self.eval(p.expression,self._context):
                    self.execute(name)
            else:
                self.execute(name)        

    def stop(self):
        self._context['__status']='stopping'
    def pause(self):
        self._context['__status']='pausing'   

    def execute(self,_key):
        if self._context['__status']=='running':            
            node=self._spec.nodes[_key]
            self._context['__current']={'name':node.name ,'type': node.type } 

            if node.type == 'start': self.nextNode(node)                 
            elif node.type == 'task': self.executeTask(node)                    
            elif node.type == 'end':  self.executeEnd(node)
            elif node.type == 'exclusiveGateway':self.nextNode(node)
            elif node.type == 'inclusiveGateway':self.executeInclusiveGateway(node)
            elif node.type == 'parallelGateway':self.executeParallelGateway(node)

            else: raise ProcessError('not found node type :'+node.type)                          

            self._context['__last']={'name':node.name ,'type': node.type}   
            
        elif self._context['__status']=='pausing':
            self._context['__status']='paused'   
        elif self._context['__status']=='stopping':
            self._context['__status']='stopped'
         
    def executeEnd(self,node):
        pass
    def executeTask(self,node):
        try:
            task = self.mgr.Task[node.task.name]
            input={}
            for p in node.task.input:
                value = self.eval(p.expression,self._context,p.type)
                input[p.name]= value 
            result=task.execute(**input)
            for i,p in enumerate(node.task.output):
                self._context[p.assig]=result[i] if type(result) is tuple else result   
        except Exception as ex:
            print(ex)
            raise
        self.nextNode(node)     
    
    # https://stackoverflow.com/questions/7207309/how-to-run-functions-in-parallel
    # https://stackoverflow.com/questions/1559125/string-arguments-in-python-multiprocessing 
    def executeParallelGateway(self,node):
        if node.key in self.gateways:
            parallels = self.gateways[node.key]
            if len(parallels)> 0:
                for p in parallels:
                    p.join()
        if len(node.transition) <= 1:
            self.nextNode(node)
        else:
            parallels=[] 
            for p in node.transition:
                t =  ParallelProcess(target=self.execute ,args=(p.target,))                
                parallels.append(t)
            self.gateways[node.key]=parallels
            for p in parallels:
                p.start()
    def executeInclusiveGateway(self,node):
        if node.key in self.gateways:
            count = self.gateways[node.key]
            if count > 1:
                count-=1
                self.gateways[node.key] = count
            else:
                if len(node.transition) <= 1:
                    self.nextNode(node)
                else:
                    self.gateways[node.key] = len(node.transition)
                    for p in node.transition:
                        if p.expression != None:
                            if self.eval(p.expression,self._context):
                                self.execute(p.target)
                        else:
                            self.execute(p.target)           
       
    def nextNode(self,node):
        for p in node.transition:
            if p.expression != None:
                if self.eval(p.expression,self._context):
                    self.execute(p.target)
                    break 
            else:
                self.execute(p.target)
                break
        
        
      
                      
  
class ProcessManager(Manager):
    def __init__(self,mgr):        
        super(ProcessManager,self).__init__(mgr)
        self._instances= {}
        self.expManager= ExpressionManager() 
        self.bpmPaser= BpmParser(mgr,self.expManager)

    def parse(self,key:str,spec:dict)-> ProcessSpec:
        spec['name'] = key
        type =spec['type']
        if type == 'bpm': return self.bpmPaser.parse(spec)
        else: raise ProcessError('not found process type :'+type) 

    def createInstance(self,spec:ProcessSpec,context:Context,parent=None)-> ProcessInstance:
        instance=None
        if spec.type == 'bpm': instance= BpmInstance(parent,spec,context,self.mgr,self.expManager)
        else: raise ProcessError('not found process type :'+spec.type)
        instance.id = str(uuid.uuid4())
        return instance

    def applyConfig(self,key,value):
        self._list[key] =self.parse(key,value)
    
    def apply(self,key:str,spec:dict,context:Context,parent=None)-> ProcessInstance:
        processSpec =self.parse(key,spec)
        self._list[key]= processSpec 
        return  self.createInstance(spec,context,parent) 
    
    def create(self,key:str,context:Context,parent=None)-> ProcessInstance:
        spec=self._list[key]
        return self.createInstance(spec,context,parent) 

    # https://www.genbeta.com/desarrollo/multiprocesamiento-en-python-threads-a-fondo-introduccion
    # https://rico-schmidt.name/pymotw-3/threading/
    def start(self,instance:ProcessInstance,sync=False):        
        try:            
            thread = threading.Thread(target=self._process_start, args=(instance,))
            self._instances[instance.id]= {"instance":instance,"thread":thread }            
            if not sync: thread.setDaemon(True)            
            thread.start()
            if sync: thread.join()            
        except Exception as ex:
            print(ex)
            raise

    def stop(self,id):
        self._instances[id]['instance'].stop() 
    def pause(self,id):
        self._instances[id]['instance'].pause()     
    def _process_start(self,instance:ProcessInstance):
        instance.start()
    def getInstance(self,id)->ProcessInstance:
        return self._instances[id]



mainManager = MainManager()
mainManager.add(ConfigManager) 
mainManager.add(TypeManager) 

mainManager.add(EnumManager)
mainManager.add(TaskManager) 
mainManager.add(ProcessManager) 

dir_path = path.dirname(path.realpath(__file__))
mainManager.loadPlugin(path.join(dir_path,'main'))
