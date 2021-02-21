from .entity import *

class Manager:
    main:None
    def __init__(self):
        self.list = {}

    def add(self,value):
        value.main = self
        key=type(value).__name__
        self.list[key]= value    

    def addConfig(self,key,value):
        self.list[key]= value

    def el(self,key):
        return self.list[key]    

    def loadConfig(self,value):
        for key in value:
            self.addConfig(key,value[key])

class Main(Manager):
    def __init__(self):
        self.main = self
        super(Main,self).__init__()

main = Main() 


################################ Type
class Type(Manager):
    def __init__(self):
        super(Type,self).__init__()
main.add(Type())         

################################ Enum
class Enum(Manager):
    def __init__(self):
        super(Enum,self).__init__()

    def addConfig(self,key,value):
        self.list[key]= EnumEntity(value['values']) 
main.add(Enum()) 

################################ Function
class Function(Manager):
    def __init__(self):
        super(Function,self).__init__()

    def addConfig(self,key,value):
        self.list[key].definition =value
      
main.add(Function())        


class FunctionEntity:
    def __init__(self,definition=None):
        self._definition=definition

    @property    
    def definition(self):
        return self._definition        

    @definition.setter    
    def definition(self,value):
        self._definition=value

    @property    
    def description(self):
        return self._definition['description'] 

    @property    
    def parameters(self):
        return self._definition['parameters'] 

    @property    
    def output(self):
        return self._definition['output']            


class CvtColor(FunctionEntity):
    def __init__(self):
        super(CvtColor,self).__init__()

main.el('Function').add(CvtColor())




################################ Activity
class Activity(Manager):
    def __init__(self):
        super(Activity,self).__init__()        
main.add(Activity())  


################################ Process

class Process(Manager):
    def __init__(self):
        super(Process,self).__init__()
main.add(Process()) 






with open('../config/main.yaml', 'r') as stream:
    try:
        data = yaml.safe_load(stream)
        for key in data:
            main.el(key).loadConfig(data[key])
    except yaml.YAMLError as exc:
        print(exc)


print(main.el('Enum').el('ColorConversionCodes').values)
print(main.el('Function').el('CvtColor').parameters)








