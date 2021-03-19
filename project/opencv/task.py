
import cv2 as cv

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

class CvtColorTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,source,code):
        return cv.cvtColor(source,code)  

class CannyTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,threshold1,threshold2):

        color = False
        if len(image.shape) >= 3:
            image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            color = True

        output = cv.Canny(image,threshold1,threshold2)
        if color: output = cv.cvtColor(output, cv.COLOR_GRAY2BGR)

        return output










class ListTest():
    def __init__(self,mgr):
        self.mgr= mgr    
    def execute(self):
        print(self.mgr.Enum.ColorConversion.values)
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
