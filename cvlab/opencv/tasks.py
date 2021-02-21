from ..process.managers import *
import cv2 as cv

class CvtColor(Task):
    def __init__(self):
        super(CvtColor,self).__init__()

    def execute(params):
        return cv.cvtColor(params['source'], params['code'])       

