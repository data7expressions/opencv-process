from .core import *
from .entity import *

class Main(Manager):
    def __init__(self):
        self.main = self
        super(Main,self).__init__()

################################ Type
class Type(Manager):
    def __init__(self):
        super(Type,self).__init__()
      

################################ Enum
class Enum(Manager):
    def __init__(self):
        super(Enum,self).__init__()

    def addConfig(self,key,value):
        self.list[key]= EnumEntity(value['values']) 


################################ Function
class Function(Manager):
    def __init__(self):
        super(Function,self).__init__()

    def addConfig(self,key,value):
        self.list[key].definition =value
 


################################ Activity
class Activity(Manager):
    def __init__(self):
        super(Activity,self).__init__()        



################################ Process

class Process(Manager):
    def __init__(self):
        super(Process,self).__init__()
