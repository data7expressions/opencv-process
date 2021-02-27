from .core import *

class Process:
    def __init__(self,mgr,parent,spec,context):        
        self.mgr=mgr
        self.parent=parent
        self.spec=spec
        self.context=context 

    def solveParams(self,params,context):
        return self.mgr['Expression'].solveParams(params,context)            

    def node(self,key):
        return self.spec['nodes'][key]    

    def start(self):
        self.init()
        self.execute('start')

    def init(self):
       if 'init' in self.spec:
           vars = self.solveParams(self.spec['init'],self.context)
           for k in vars:
                self.context['vars'][k]=vars[k] 

    def restart(self):
        self.execute(self.context.current)

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
            taskManager = self.mgr.get('Task',node['task'])
            input = self.solveParams(node['input'],self.context)
            result=taskManager.execute(**input)
            if 'output' in node:
                self.context['vars'][node['output']]=result  
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def nextNode(self,node):
        if 'transition' not in node: return        
        transition = node['transition']        
        if type(transition) is str:self.execute(transition) 
        elif type(transition) is list: 
            for p in transition:self.execute(p) 
        elif type(transition) is dict: 
            for k in transition:self.execute(transition[k])

class ProcessManager(Manager):
    def __init__(self,mgr):
        self._instances= []
        super(ProcessManager,self).__init__(mgr)    

    def start(self,key,context):
        spec=self.list[key]
        instance=Process(self.mgr,self,spec,context)
        self._instances.append(instance)
        instance.start()