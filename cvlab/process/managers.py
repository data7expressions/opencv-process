from .core import *
import sys
import yaml

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
        if type(expresion).__name__ == 'str' and expresion.startswith('$'):
            variable=expresion.replace('$','')
            return context['vars'][variable]
        return expresion

    def solveParams(self,params,context):
        result={}    
        for key in params:
            expression = params[key]
            result[key] = self.solveExpression(expression,context) 
        return result

    def applyConfig(self,configPath):
        with open(configPath, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                for key in data:
                    self.get(key).loadConfig(data[key])
            except yaml.YAMLError as exc:
                print(exc)       

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
    def __init__(self,main,parent,spec,context):        
        self._main=main
        self._parent=parent
        self._spec=spec
        self._context=context         

    def node(self,key):
        return self._spec['nodes'][key]    

    def start(self):
        self.execute('start')

    def restart(self):
        self.execute(self._context.current)

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
            taskManager = self._main.manager('Task',node['task'])
            params = self._main.solveParams(node['params'],self._context)
            result=taskManager.execute(params)
            if "output" in node:
                self._context['vars'][node['output']]=result  
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def nextNode(self,node):
        next=list(node['transitions'].keys())[0]
        self.execute(next)      

class ProcessManager(Manager):
    def __init__(self):
        self._instances= []
        super(ProcessManager,self).__init__()    

    def start(self,key,context):
        spec=self.list[key]
        instance=Process(self._main,self,spec,context)
        self._instances.append(instance)
        instance.start()