from ..core import *
import cv2 as cv

class CvtColor(Task):
    def __init__(self):
        super(CvtColor,self).__init__()
    def execute(self,source,code):
        return cv.cvtColor(source,code)       

class ImRead(Task):
    def __init__(self):
        super(ImRead,self).__init__()
    def execute(self,filename):
        return cv.imread(filename) 

class ImWrite(Task):
    def __init__(self):
        super(ImWrite,self).__init__()
    def execute(self,filename,img):
        return cv.imwrite(filename,img)

