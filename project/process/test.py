class ListTest():
    def __init__(self,mgr):
        self.mgr= mgr    
    def execute(self):
        print(self.mgr.get('Enum','ColorConversion').values)
        print(self.mgr.get('Task','CvtColor').input)

class ProcessTest():
    def __init__(self,mgr):
        self.mgr= mgr    
    def execute(self):

        context = {'vars':{'source':'/home/flavio/develop/opencv-process/data/workspace/data/source.jpg'
                          ,'target':'/home/flavio/develop/opencv-process/data/workspace/data/source.jpg'}
                  }
        self.mgr['Process'].start('test',context)
