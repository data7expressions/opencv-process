
import cv2 as cv
import numpy as np  

cvtypes = {
    "uint8": cv.CV_8U,
    "uint16": cv.CV_16U,
    "int8": cv.CV_8S,
    "int16": cv.CV_16S,
    "float32": cv.CV_32F,
    "float64": cv.CV_64F
}

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

class BlurTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,ratio):        
        return cv.blur(image, (ratio, ratio))

class GaussianBlurTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,kernel,sigma):        
        return cv.GaussianBlur(image,(kernel,kernel), sigma) 

class GaussianBlur3DTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,kernel,coordinate,borderType):        
        image = np.copy(image)
        for z in image:
            cv.GaussianBlur(z, (kernel, kernel), coordinate['x'], z, coordinate['y'], borderType)
        for y in range(image.shape[1]):
            xz = image[:, y]
            cv.GaussianBlur(xz, (1, kernel), 0, xz, coordinate['z'], borderType)
        return image

class InRangeTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,min,max):
        image = np.copy(image)
        return cv.inRange(image, min, max)   

class ColorNormalizerTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,outmean=128,outstddev=64):
        mean, stddev = cv.meanStdDev(image)
        if stddev == 0: stddev = 1
        output = (image.astype(np.float32) - mean) * (outstddev/stddev) + outmean
        return np.clip(output, 0, 255).astype(image.dtype)

class ContrastChangeTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,factor):
        avg = cv.mean(image)
        output = cv.add(cv.subtract(np.float64(image), avg) * factor, avg)
        return cv.add(np.zeros(output.shape, image.dtype), output, dtype=cvtypes[image.dtype.name])

class MorphologyExTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,operation,elementType,elementSize,iterations):
        image = np.copy(image)
        element = cv.getStructuringElement(elementType, (elementSize, elementSize))
        return cv.morphologyEx(image, operation, element, iterations=iterations,)

class DilateTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,elementType,elementSize,iterations):
        image = np.copy(image)
        element = cv.getStructuringElement(elementType, (elementSize, elementSize))
        return cv.dilate(image, element, iterations=iterations)

class ErodeTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image,elementType,elementSize,iterations):
        image = np.copy(image)
        element = cv.getStructuringElement(elementType, (elementSize, elementSize))
        return cv.erode(image, element, iterations=iterations)   

class CvAddTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image1,image2):
        output=None
        cv.add(image1, image2, output)        
        return output

class CvAddsTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,images):
        output=None
        first= True
        for input in images:
            if first:
                output = input
                first=False
            else:
                cv.add(output, input, output)
        return output

class CvSubtractTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image1,image2):
        return cv.subtract(image1,image2) 

class CvAbsdiffTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,image1,image2):
        return cv.absdiff(image1, image2)

# Pendings AverageOperator,MaxOperator,MinOperator,InvertOperator,ScalarMultiplyOperator,ScalarAddOperator 

class VideoCaptureTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,number):
        return cv.VideoCapture(number)

class VideoReadTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,cam):
        if cam.isOpened():
            return cam.read()  

class VideoReleaseTask():
    def __init__(self,mgr):
        self.mgr=mgr
    def execute(self,cam):
        cam.release()