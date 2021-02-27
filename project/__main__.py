
from tkinter import *
from .core import *
from .process import *
from .extensions.opencv import *
from .test.opencv import *
from .ui.main import *
import os

mgr = MainManager() 
mgr.context={ 'workspace' : (path.join(getcwd(),'data/workspace')) }

def init():
   # TODO: ver como cargar esto dinamicamente utilizando reflexion
   mgr.add(TypeManager)
   mgr.add(EnumManager)       
   mgr.add(TaskManager) 
   mgr.add(ProcessManager)
   mgr.add(ExpressionManager) 
   mgr.add(UiManager) 

   mgr['Task'].add(CvtColor)
   mgr['Task'].add(ImRead)
   mgr['Task'].add(ImWrite)

   rootpath = os.getcwd()
   mgr.applyConfig(os.path.join(rootpath,'project/core.yaml'))
   mgr.applyConfig(os.path.join(rootpath,'project/extensions/opencv.yaml'))
   mgr.applyConfig(os.path.join(rootpath,'data/workspace/process.yaml'))

def main():
    tk = Tk()
    mgr['Ui'].add(MainUi)
    mgr['Ui'].add(ImageUi)
    
   
    mgr['Ui'].init()
    mainUi =mgr['Ui'].new('Main',(tk,mgr))
    mainUi.init()
    mainUi.mainloop()

def test():
    TestList(mgr).execute()
    TestProcess(mgr).execute()

if __name__ == '__main__':
    init()
    main()