from ..process.managers import *

class TestProcess():
    def __init__(self,main):
        self.main= main    
    def execute(self):
        print(self.main.manager('Enum','Cv_ColorConversionCodes').values)
        print(self.main.manager('Task','Cv_CvtColor').params)
        
        
        
        context = {'vars':{'source':'/home/flavio/develop/opencv-lab/workspace/data/source.jpg'
                          ,'target':'/home/flavio/develop/opencv-lab/workspace/data/source.jpg'}
                  }
        self.main.get('Process').start('test',context)