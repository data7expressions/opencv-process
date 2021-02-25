import sys
import yaml

class ChildManager:

    def __init__(self,mgr=None,parent=None):        
        self.mgr=mgr
        self.parent=parent

    def set(self,mgr,parent):
        self.mgr=mgr
        self.parent=parent

class Manager(ChildManager):
    def __init__(self,mgr=None,parent=None):
        self.list = {}
        super(Manager,self).__init__(mgr,parent)   

    def add(self,value):
        value.set(self.mgr,self)
        key=type(value).__name__
        self.list[key]= value    

    def addConfig(self,key,value):
        self.list[key]= value

    def loadConfig(self,value):
        for key in value:
            self.addConfig(key,value[key])    

    def __getitem__(self,key):
        return self.list[key]  

    def list(self):
        return self.list 

class MainManager(Manager):
    def __init__(self):
        self.mgr = self
        super(MainManager,self).__init__()

    def add(self,value):
        value.set(self,self)
        key=type(value).__name__.replace('Manager','')
        self.list[key]= value 

    def get(self,type,key):
        return self[type][key]  

    def applyConfig(self,configPath):
        with open(configPath, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                for key in data:
                    self[key].loadConfig(data[key])
            except yaml.YAMLError as exc:
                print(exc) 

class ExpressionManager(Manager):
    def __init__(self):
        super(ExpressionManager,self).__init__()

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
# Type -------------------------------------
class TypeManager(Manager):
    def __init__(self):
        super(TypeManager,self).__init__()
      
# Enum -------------------------------------
class Enum():
    def __init__(self,values):
        self.values =values

    def values(self):
        return self.values
    
    def value(self,key):
        return self.values[key]

class EnumManager(Manager):
    def __init__(self):
        super(EnumManager,self).__init__()

    def addConfig(self,key,value):
        self.list[key]= Enum(value) 

# Task -------------------------------------
class Task(ChildManager):
    def __init__(self,spec=None,mgr=None,parent=None):
        self.spec=spec
        super(Task,self).__init__(mgr,parent)
  
    def setSpec(self,value):
        self.spec=value

    @property
    def input(self):
        return self.spec['input'] 
    @property
    def output(self):
        return self.spec['output']                

class TaskManager(Manager):
    def __init__(self):
        super(TaskManager,self).__init__()

    def addConfig(self,key,value):
        self.list[key].setSpec(value)    
    

