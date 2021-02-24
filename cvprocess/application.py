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

        self.main.get('Task').add(CvtColor())
        self.main.get('Task').add(ImRead())
        self.main.get('Task').add(ImWrite())

        rootpath = os.getcwd()
        self.main.applyConfig(os.path.join(rootpath,'cvprocess/process/core.yaml'))
        self.main.applyConfig(os.path.join(rootpath,'cvprocess/opencv/opencv.yaml'))
        self.main.applyConfig(os.path.join(rootpath,'workspace/process.yaml'))

        

