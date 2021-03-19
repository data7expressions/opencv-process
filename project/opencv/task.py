
import cv2 as cv
import numpy as np  

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
        return cv.cvtColor(output, cv.COLOR_GRAY2BGR) if color else output       

class RotateTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,angle):
        image = np.copy(image)
        angle_rad = np.radians(angle)
        h, w = image.shape[:2]
        trans1 = np.array([[1, 0, -w / 2],
                           [0, 1, -h / 2],
                           [0, 0, 1]],
                          dtype=np.float32)
        if angle % 180 == 90:
            h, w = w, h
        trans2 = np.array([[1, 0, w / 2],
                           [0, 1, h / 2],
                           [0, 0, 1]],
                          dtype=np.float32)
        rot = np.array([[np.cos(angle_rad), -np.sin(angle_rad), 0],
                        [np.sin(angle_rad), np.cos(angle_rad), 0],
                        [0, 0, 1]],
                          dtype=np.float32)

        mat = np.dot(np.dot(trans2, rot), trans1)
        return cv.warpAffine(image, mat[:2], (w, h))

class ResizeTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,percent):        
        width = int(image.shape[1] * percent / 100)
        height = int(image.shape[0] * percent / 100)
        dim = (width, height)
        return cv.resize(image, dim, interpolation = cv.INTER_AREA)

# TODO: no funciona, revisar
class CropTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,rectangle:dict):        
        cw = int(image.shape[1] * rectangle['x'])
        w2 = rectangle['width'] // 2
        ch = int(image.shape[0] * rectangle['y'])
        h2 = rectangle['height'] // 2
        return image[max(0, ch - h2):ch + h2, max(0, cw - w2):cw + w2]

