from .process.core import *
from .process.managers import *
from .opencv.tasks import *
import os

class Aplication():
    def __init__(self, ui,main):
        self.ui = ui
        self.main= main

    def init(self):
        self.initManager()
        self.ui.init()     

    def initManager(self):

        self.main = MainManager()
        self.main.add(TypeManager())
        self.main.add(EnumManager())       
        self.main.add(TaskManager()) 
        self.main.add(ProcessManager()) 

        self.main.get('Task').add(Cv_CvtColor())
        self.main.get('Task').add(Cv_ImRead())
        self.main.get('Task').add(Cv_ImWrite())

        rootpath = os.getcwd()
        self.main.applyConfig(os.path.join(rootpath,'cvlab/process/core.yaml'))
        self.main.applyConfig(os.path.join(rootpath,'cvlab/opencv/opencv.yaml'))
        self.main.applyConfig(os.path.join(rootpath,'workspace/process.yaml'))

        print(self.main.manager('Enum','Cv_ColorConversionCodes').values)
        print(self.main.manager('Task','Cv_CvtColor').params)
        context = {'vars':{}}
        self.main.get('Process').start('test',context)