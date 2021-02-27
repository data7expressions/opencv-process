from ..core import *
import cv2 as cv

class CvtColor(Task):
    def __init__(self,mgr):
        super(CvtColor,self).__init__(mgr)
    def execute(self,source,code):
        return cv.cvtColor(source,code)       

class ImRead(Task):
    def __init__(self,mgr):
        super(ImRead,self).__init__(mgr)
    def execute(self,filename):
        return cv.imread(filename) 

class ImWrite(Task):
    def __init__(self,mgr):
        super(ImWrite,self).__init__(mgr)
    def execute(self,filename,img):
        return cv.imwrite(filename,img)

