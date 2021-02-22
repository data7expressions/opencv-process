from .core import *

class MainManager(Manager):
    def __init__(self):
        self._main = self
        super(MainManager,self).__init__()

    def add(self,value):
        value.main = self
        value.parent = self
        key=type(value).__name__.replace('Manager','')
        self.list[key]= value 

    def manager(self,type,key):
        return self.get(type).get(key)

    def solveExpression(self,expresion,context):
        if expresion.startswith('$'):
            variable=expresion.replace('$','')
            return context.vars[variable]
        return expresion

    def solveParams(self,params,context):
        result={}    
        for key in params:
            expression = params[key]
            result[key] = self.solveExpression(expression,context) 
        return result    

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
# class Node():
#     def __init__(self,spec=None):
#         self._spec=spec

#     @property    
#     def spec(self):
#         return self._spec        

#     @spec.setter    
#     def spec(self,value):
#         self._spec=value

# class StartNode(Node):
#     def __init__(self):
#         super(StartNode,self).__init__()

# class EndNode(Node):
#     def __init__(self):
#         super(EndNode,self).__init__()    
    
# class TaskNode(Node):
#     def __init__(self):
#         super(TaskNode,self).__init__() 

#     def execute(self,process,node):
#         taskManager = self._main.manager('Task',node.task)
#         params = self._main.solveParams(node.params,process.context)
#         result=taskManager.execute(params)
#         if node.output!=None:
#             process.context.vars[node.output]=result  

#         for key in node.transitions:
#             transition=node.transitions[key]
            
         

# class NodeManager(Manager):
#     def __init__(self):
#         super(NodeManager,self).__init__() 
#     def addConfig(self,key,value):
#         self.list[key].spec =value 



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

    def execute(self,params):
        return None       

class TaskManager(Manager):
    def __init__(self):
        super(TaskManager,self).__init__()

    def addConfig(self,key,value):
        self.list[key].spec =value

################################ Process

class Process:
    def __init__(self,spec,main,parent):
        self._spec=spec
        self._main=main
        self._parent=parent        

    def node(self,key):
        return self._spec['nodes'][key]    

    def start(self,context):
        self.execute('start',context)

    def restart(self,context):
        self.execute(context.current,context)



    def nextNode(self,node,context):
        next=list(node['transitions'].keys())[0]
        self.execute(next,context)

    def execute(self,key,context):
        node=self.node(key)
        type=node['type'] 
        if type == 'Start':
            self.nextNode(node,context)
        elif type == 'End':
            self.executeEnd(node,context)               
        elif type == 'Task':
            self.executeTask(node,context)
            self.nextNode(node,context)
          
    def executeEnd(self,node,context):
        print('End')

    def executeTask(self,node,context):
        taskManager = self._main.manager('Task',node['task'])
        params = self._main.solveParams(node['params'],context)
        result=taskManager.execute(params)
        if node['output']!=None:
            context.vars[node['output']]=result  

          

    

# class ProcessInstance:
#     def __init__(self,spec,context):
#         self._spec=spec
#         self._context=context 

#     def start(self):
#         nodes= self._spec.nodes
#         node=self._context.current==None if nodes['start'] else nodes[self._context.current]
#         self.execute(node)    

#     def execute(self,node):
#         self.current=node
#         manager=self._main.manager('Node',node.node)
#         manager.execute(self,node)

   

class ProcessManager(Manager):
    def __init__(self):
        super(ProcessManager,self).__init__()

    def addConfig(self,key,value):
        self.list[key]= Process(value,self._main,self)