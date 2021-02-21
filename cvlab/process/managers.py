from .core import *

class MainManager(Manager):
    def __init__(self):
        self.main = self
        super(MainManager,self).__init__()

    def add(self,value):
        value.main = self
        key=type(value).__name__.replace('Manager','')
        self.list[key]= value     

################################ Type
class TypeManager(Manager):
    def __init__(self):
        super(TypeManager,self).__init__()
      

################################ Enum
class Enum():
    def __init__(self,values):
        self._values =values

    @property
    def values(self):
        return self._values

class EnumManager(Manager):
    def __init__(self):
        super(EnumManager,self).__init__()

    def addConfig(self,key,value):
        self.list[key]= Enum(value) 

################################ Process Node
class Node():
    def __init__(self,spec=None):
        self._spec=spec

    @property    
    def spec(self):
        return self._spec        

    @spec.setter    
    def spec(self,value):
        self._spec=value

class StartNode(Node):
    def __init__(self):
        super(StartNode,self).__init__()

class EndNode(Node):
    def __init__(self):
        super(EndNode,self).__init__()    
    
class TaskNode(Node):
    def __init__(self):
        super(TaskNode,self).__init__() 

class NodeManager(Manager):
    def __init__(self):
        super(NodeManager,self).__init__() 
    def addConfig(self,key,value):
        self.list[key].spec =value 



################################ Task
class Task():
    def __init__(self,spec=None):
        self._spec=spec

    @property    
    def spec(self):
        return self._spec        

    @spec.setter    
    def spec(self,value):
        self._spec=value

    @property    
    def description(self):
        return self._spec['description'] 

    @property    
    def params(self):
        return self._spec['params'] 

    @property    
    def output(self):
        return self._spec['output']   

class TaskManager(Manager):
    def __init__(self):
        super(TaskManager,self).__init__()

    def addConfig(self,key,value):
        self.list[key].spec =value

################################ Process

class Process:
    def __init__(self,spec=None):
        self._spec=spec
    

class ProcessInstance:
    def __init__(self,spec,context):
        self._spec=spec
        self._context=context 

    def start(self):
        nodes= self._spec.nodes
        node=None
        if self._context.current==None:
            node=next(p for p in nodes if p.type == 'Start')
        else:
            node=next(p for p in nodes if p.name == self._context.current)

        self.execute(node)    

    def execute(self,node):
        self.current=node
        manager=self.nodeManager(node.type)
        manager.execute(node)

class ProcessManager(Manager):
    def __init__(self):
        super(ProcessManager,self).__init__()

    def addConfig(self,key,value):
        self.list[key]= Process(value)