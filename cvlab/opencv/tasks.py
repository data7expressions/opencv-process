from ..process.managers import *
import cv2 as cv

class Cv_CvtColor(Task):
    def __init__(self):
        super(Cv_CvtColor,self).__init__()

    def execute(self,params):
        return cv.cvtColor(params['source'], params['code'])       

class Cv_ImRead(Task):
    def __init__(self):
        super(Cv_ImRead,self).__init__()

    def execute(self,params):
        return cv.imread(params['filename']) 

class Cv_ImWrite(Task):
    def __init__(self):
        super(Cv_ImWrite,self).__init__()

    def execute(self,params):
        return cv.imwrite(params['filename'],params['img'])

