
import cv2 as cv

class CvtColorTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,source,code):
        return cv.cvtColor(source,code)       

class ImReadTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,filename):
        return cv.imread(filename) 

class ImWriteTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,filename,img):
        return cv.imwrite(filename,img)

class ListTest():
    def __init__(self,mgr):
        self.mgr= mgr    
    def execute(self):
        print(self.mgr['Enum']['ColorConversion'].values)
        print(self.mgr['Config']['Task']['CvtColor']['input'])
class ProcessTest():
    def __init__(self,mgr):
        self.mgr= mgr    
    def execute(self):

        context = {'vars':{'source':'/home/flavio/develop/opencv-process/data/workspace/data/source.jpg'
                          ,'target':'/home/flavio/develop/opencv-process/data/workspace/data/target.jpg'}
                  }
        self.mgr['Process'].start('test',context)  