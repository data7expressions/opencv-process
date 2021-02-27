import sys
import yaml

class Helper:
    @staticmethod
    def rreplace(s, old, new, occurrence=1):
        li = s.rsplit(old, occurrence)
        return new.join(li)

# class ChildManager:
#     def set(self,mgr):
#         self.mgr=mgr
#         self.context={}

class Manager():
    def __init__(self,mgr):
        self.list = {}
        self.mgr=mgr

    def add(self,type):        
        self.list[type.__name__]= type(self.mgr)  
          

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
        self._context={}
        super(MainManager,self).__init__(self)

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self,value):
        self._context=value


    def add(self,type):
        key = Helper.rreplace(type.__name__, 'Manager', '')   
        self.list[key]= type(self)       

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
    def __init__(self,mgr):
        super(ExpressionManager,self).__init__(mgr)

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

class Task():
    def __init__(self,mgr):
        self.mgr=mgr
 
    def setSpec(self,value):
        self.spec=value

    @property
    def input(self):
        return self.spec['input'] 
    @property
    def output(self):
        return self.spec['output']                

class TaskManager(Manager):
    def __init__(self,mgr):
        super(TaskManager,self).__init__(mgr)

    def addConfig(self,key,value):
        self.list[key].setSpec(value)    



