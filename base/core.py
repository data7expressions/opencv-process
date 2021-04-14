from py_mgr.core import Manager
from py_process.core import Process,ProcessInstance, ProcessSpec
from py_expression.core import Exp

class EnumManager(Manager):
    def __init__(self,mgr):
        super(EnumManager,self).__init__(mgr)
        self.exp = Exp()

    def applyConfig(self,_key,value):
        self.addEnum(_key,value['values'])

    def addEnum(self,name,values:dict):
        self.exp.addEnum(name,values)

    def getEnum(self,name):
        return self.exp.getEnum(name)   

class ProcessManager(Manager):
    def __init__(self,mgr):
        super(ProcessManager,self).__init__(mgr)
        self.process = Process()

    def applyConfig(self,key,value):
        self.process.addSpec(key,value)   

    def getSpec(self,key)-> ProcessSpec:
        return self.process.getSpec(key)          

    def create(self,key:str,context:dict,parent=None)-> ProcessInstance:
        return self.process.create(key,context,parent)

    def start(self,instance:ProcessInstance,sync=False):        
        self.process.start(instance,sync)

    def stop(self,id):
        self.process.stop(id)

    def pause(self,id):
        self.process.pause(id)    

    def getInstance(self,id)->ProcessInstance:
        return self.process.getInstance(id) 