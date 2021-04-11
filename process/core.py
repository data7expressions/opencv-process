from mgr.base import *
from py_expression.core import Exp
import uuid
import threading

import yaml
from os import path
import glob
import importlib.util
import inspect
from multiprocessing import Process as ParallelProcess, process

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

# class TaskManager(Manager):
#     def __init__(self,mgr):
#         super(TaskManager,self).__init__(mgr)  

# class EnumManager(Manager):
#     def __init__(self,mgr):
#         super(EnumManager,self).__init__(mgr)
#         self.exp = Exp()

#     def applyConfig(self,_key,value):
#         self.addEnum(_key,value['values'])

#     def addEnum(self,name,values:dict):
#         self.exp.addEnum(name,values)
#     def getEnum(self,name):
#         return self.exp.getEnum(name)     


class ProcessError(Exception):pass
class Object(object):pass
class ProcessSpec(object):pass
class Token(object):pass

"""
para la implementacion de python se usara un diccionario para almacenar
pero para la implementacion en go usar REDIS
"""
class TokenManager(Manager):
    def __init__(self,mgr):
        super(TokenManager,self).__init__(mgr)

    def create(self,process,parent=None,node=None,status='running')->Token:
        token = Token()
        token.id= str(uuid.uuid4())
        token.process= process,
        token.mainId = parent.mainId if parent!= None else token
        token.parentId = parent.id if parent!= None else token
        token.status= status
        token.node = node
        token.childs = []
        return self.set(token.id,token)

    def set(self,token:Token):
        self._list[token.id] = token
        return token

    def get(self,key:str)-> Token:
        return self._list[key]

    def getChilds(self,parentId):
        parent = self.get(parentId)
        list = []
        for childId in parent.childs:
            list.append(self.get(childId))
        return list

    def update(self,token,data:dict):        
        for p in data:
            setattr(token, p,data[p])
        return self.set(token) 

    def delete(self,id:str):
        del self._list[id]

    def deleteChilds(self,parent):
        for childId in parent.childs:
            self.delete(childId)
        parent.childs = []
        return self.set(parent)    
 




class BpmParser:
    def __init__(self,mgr,exp):
        self.mgr = mgr
        self.exp = exp     

    def parse(self,spec:dict)-> ProcessSpec:
        process = ProcessSpec()
        process.name= spec['name']
        process.type= spec['type']
        process.bind = spec['bind'] if 'bind' in spec else []
        process.input=self.parseInput(spec) 
        process.declare=self.parseDeclare(spec)
        process.init=self.parseInit(spec)  
        process.vars=self.getVars(process)
        process.nodes = {}        
        for key in spec['nodes']:
            specNode=spec['nodes'][key]
            specNode['name']=key
            process.nodes[key] =self.parseNode(specNode)
        for key in process.nodes:
            node=process.nodes[key]
            node.entries= self.getEntries(key,process.nodes)
        return process    

    def parseInput(self,spec:dict):
        input = []
        if 'input' in spec:
            for p in spec['input']:
                param  = Object()
                param.name = p
                param.type = spec['input'][p]
                input.append(param)
        return input         

    def parseDeclare(self,spec:dict):
        declare = []
        if 'declare' in spec:
            for p in spec['declare']:
                param  = Object()
                param.name = p
                param.type = spec['declare'][p]
                declare.append(param)
        return declare 

    def parseInit(self,spec:dict):
        init = {}
        if 'init' in spec:
            init.expression = self.exp.parse(spec['init']['exp'])           
        return init                                

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
    
    def getEntries(self,key,nodes):
        list = []
        for name in nodes:
            node=nodes[name]
            for t in node.transition:
                if t.target == key:
                    s = Object()
                    s.source= node
                    s.transition = t
                    list.append(s) 
        return list  

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
        node.expression = self.exp.parse(spec['exp']) if 'exp' in spec else None
        return node

    def parseNodeTask(self,spec):        
        node= self.parseNodeDefault(Object(),spec)
        node.expression= self.exp.parse(spec['exp']) if 'exp' in spec else None 
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
                item.expression = self.exp.parse(p['exp']) if 'exp' in p else None
                transition.append(item)
        return transition        

class ProcessInstance:
    def __init__(self,spec:ProcessSpec,context:Context,mgr:MainManager,exp:Exp):
        self._id=None 
        self._context=context
        self._status='ready'
        self._spec=spec      
        self.mgr=mgr
        self.exp = exp 
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
        if 'init' in self._spec and 'expression' in self._spec.init:
            self.exp.eval(self._spec.init.expression,self._context)

class BpmInstance(ProcessInstance):
    def __init__(self,parent:str,spec:ProcessSpec,context:Context,mgr:MainManager,exp:Exp):
        super(BpmInstance,self).__init__(parent,spec,context,mgr,exp)   

    
    def start(self,parent=None):
        self._status='running'        
        
        starts = dict(filter(lambda p: p[1].type == 'start', self._spec.nodes.items()))
        target=None
        for name in starts:
            p = starts[name]
            if p.expression != None:
                if self.exp.eval(p.expression,self._context):
                    target= name
                    break
            else:
                target= name
                break 

        if target == None: raise ProcessError('not found start node enabled')         
        token=self.mgr.Token.create(process=self._spec.name,parent=parent,node=target)             
        self.execute(token)    


    def stop(self):
        self._status='stopping'
    def pause(self):
        self._status='pausing'   

    def execute(self,token):
        if self._status=='running':            
            node=self._spec.nodes[token.node]
            
            # self._context['__current']={'name':node.name ,'type': node.type } 

            if node.type == 'start': self.nextNode(node,token)                 
            elif node.type == 'task': self.executeTask(node,token)                    
            elif node.type == 'end':  self.executeEnd(node,token)
            elif node.type == 'exclusiveGateway':self.nextNode(node,token)
            elif node.type == 'inclusiveGateway':self.executeInclusiveGateway(node,token)
            elif node.type == 'parallelGateway':self.executeParallelGateway(node,token)

            else: raise ProcessError('not found node type :'+node.type)                          

            # self._context['__last']={'name':node.name ,'type': node.type}   
            
        elif self._status=='pausing':
            self._status='paused'   
        elif self._status=='stopping':
            self._status='stopped'
         
    def executeEnd(self,node,token):
        token=self.mgr.Token.update(token,{'status':'end'})
    def executeTask(self,node,token):
        try:
            self.exp.eval(node.expression,self._context)
        except Exception as ex:
            print(ex)
            raise
        self.nextNode(node,token)  

    def executeInclusiveGateway(self,node,token):
        subToken=False
        pending = False
        if len(node.entries) > 1:
            if token.parentId != None:
                childs = self.mgr.Token.getChilds(token.parentId) 
                subToken=True
                token=self.mgr.Token.update(token,{'status':'end'})                
                for child in childs:
                    if child.id != token.id and child.status != 'end':
                        pending=True
                        break
        if subToken:
            if pending: return
            else: 
                parent = self.mgr.Token.get(token.parentId) 
                parent = self.mgr.Token.deleteChilds(parent)        
                token = parent
        targets=self.getTargets(node,onlyFirst=False)       
        if len(targets) == 1:
            token=self.mgr.Token.update(token,{'node':targets[0],'status':'ready'}) 
            self.execute(token)
        else:
            for target in targets:
               child=self.mgr.Token.create(process=self._spec.name,parent=token,node=target)
               token.childs.append(child)
            token=self.mgr.Token.update(token,{'childs':token.childs,'status':'await'})   
            for child in token.childs:
                self.execute(token)

    # https://stackoverflow.com/questions/7207309/how-to-run-functions-in-parallel
    # https://stackoverflow.com/questions/1559125/string-arguments-in-python-multiprocessing 
    def executeParallelGateway(self,node,token):

        subToken=False
        pending = False
        if len(node.entries) > 1:
            if token.parentId != None:
                childs = self.mgr.Token.getChilds(token.parentId) 
                if len(childs) > 1 :
                    subToken=True
                    token=self.mgr.Token.update(token,{'status':'end'})
                    token.thread.join()               
                    for child in childs:
                        if child.id != token.id and child.status != 'end':
                            pending=True
                            break
        if subToken:
            if pending: return
            else:
                parent = self.mgr.Token.get(token.parentId) 
                parent = self.mgr.Token.deleteChilds(parent)        
                token=parent
        targets=self.getTargets(node,onlyFirst=False)       
        if len(targets) == 1:
            token=self.mgr.Token.update(token,{'node':targets[0],'status':'ready'}) 
            self.execute(token)
        else:
            for target in targets:
               child=self.mgr.Token.create(process=self._spec.name,parent=token,node=target)             
               thread =  ParallelProcess(target=self.execute ,args=(token,))
               child=self.mgr.Token.update(child,{'thread':thread})
               token.childs.append(child)
            token=self.mgr.Token.update(token,{'childs':token.childs,'status':'await'})     
            for child in token.childs:
                child.thread.start()
       
    def nextNode(self,node,token):
        targets=self.getTargets(node)
        token=self.mgr.Token.update(token,{'node':targets[0] })              
        self.execute(token)        
        
    def getTargets(self,node,onlyFirst=True):
        targets=[]
        for p in node.transition:
            if p.expression != None:
                if self.exp.eval(p.expression,self._context):
                    targets.append(p.target)
                    if onlyFirst:break 
            else:
                targets.append(p.target)
                if onlyFirst:break

        if len(targets) == 0:
            raise ProcessError('node '+node.name+' not found targets')         
        return targets            
      
                      
  
class ProcessManager(Manager):
    def __init__(self,mgr):        
        super(ProcessManager,self).__init__(mgr)
        self._instances= {}
        self.exp= Exp() 
        self.bpmPaser= BpmParser(mgr,self.exp)

    def parse(self,key:str,spec:dict)-> ProcessSpec:
        spec['name'] = key
        type =spec['type']
        if type == 'bpm': return self.bpmPaser.parse(spec)
        else: raise ProcessError('not found process type :'+type) 

    def createInstance(self,spec:ProcessSpec,context:Context,parent=None)-> ProcessInstance:
        instance=None
        if spec.type == 'bpm': instance= BpmInstance(parent,spec,context,self.mgr,self.exp)
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
mainManager.add(TokenManager)

# mainManager.add(EnumManager)
# mainManager.add(TaskManager) 
mainManager.add(ProcessManager) 

dir_path = path.dirname(path.realpath(__file__))
mainManager.loadPlugin(path.join(dir_path,'main'))
