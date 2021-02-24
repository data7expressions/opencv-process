
from tkinter import *
from .core import *
from .process import *
from .extensions.opencv import *
from .test.opencv import *
from .ui.main import *
import os

mgr = MainManager() 

def init():
   mgr.add(TypeManager())
   mgr.add(EnumManager())       
   mgr.add(TaskManager()) 
   mgr.add(ProcessManager())
   mgr.add(ExpressionManager()) 

   mgr['Task'].add(CvtColor())
   mgr['Task'].add(ImRead())
   mgr['Task'].add(ImWrite())

   rootpath = os.getcwd()
   mgr.applyConfig(os.path.join(rootpath,'project/core.yaml'))
   mgr.applyConfig(os.path.join(rootpath,'project/extensions/opencv.yaml'))
   mgr.applyConfig(os.path.join(rootpath,'data/workspace/process.yaml'))

def main():
    base = Tk()
    mainUi = MainUi(base,mgr)       
    application = Aplication(mainUi,mgr)
    application.init()
    base.mainloop()

def test():
    TestList(mgr).execute()
    TestProcess(mgr).execute()

init()
test()