
import cv2 as cv

#TODO: se debe importar esta clase desde un paquete
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

class CvtColorTask(Task):
    def __init__(self,mgr):
        super(CvtColorTask,self).__init__(mgr)
    def execute(self,source,code):
        return cv.cvtColor(source,code)       

class ImReadTask(Task):
    def __init__(self,mgr):
        super(ImReadTask,self).__init__(mgr)
    def execute(self,filename):
        return cv.imread(filename) 

class ImWriteTask(Task):
    def __init__(self,mgr):
        super(ImWriteTask,self).__init__(mgr)
    def execute(self,filename,img):
        return cv.imwrite(filename,img)

