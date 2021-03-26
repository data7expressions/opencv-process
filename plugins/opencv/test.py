
class ListTest():
    def __init__(self,mgr):
        self.mgr= mgr    
    def execute(self):
        print(self.mgr.Exp.getEnum('ColorConversion'))
        print(self.mgr.Config.Task['CvtColor']['input'])

class ProcessTest():
    def __init__(self,mgr):
        self.mgr= mgr    
    def execute(self):


        init = {'source':'/home/flavio/develop/opencv-process/data/workspace/data/source.jpg'
               ,'target':'/home/flavio/develop/opencv-process/data/workspace/data/target.jpg'
               }
                  
                 
        process = self.mgr.Process.create('test',init)
        process.context.onChange += self.onChange
        self.mgr.Process.start(process.id) 


    def onChange(self,key,value,oldValue):
        print(key+' value: '+str(value)) 
