
from tkinter import *
from .core import *
from .process.manager import *
from .process.test import *
from .opencv.task import *
from .ui import *
from os import path,getcwd,listdir

mgr = MainManager() 
mgr.context={ 'workspace' : (path.join(getcwd(),'data/workspace')) }

def init():
   # TODO: ver como cargar esto dinamicamente utilizando reflexion
   mgr.add(TypeManager)
   mgr.add(EnumManager)       
   mgr.add(TaskManager) 
   mgr.add(ExpressionManager) 
   mgr.add(TestManager)
   mgr.add(UiManager) 

#    mgr.add(ProcessManager)
#    mgr['Task'].add(CvtColor)
#    mgr['Task'].add(ImRead)
#    mgr['Task'].add(ImWrite)

   rootpath = getcwd()
   mgr.applyConfig(path.join(rootpath,'project/type.yaml'))
   mgr.applyConfig(path.join(rootpath,'project/opencv/enum.yaml'))

   mgr.loadPlugins(path.join(rootpath,'project'))

   mgr.applyConfig(path.join(rootpath,'project/opencv/task.yaml'))
   mgr.applyConfig(path.join(rootpath,'data/workspace/process.yaml'))

def main():
    tk = Tk()
    mgr['Ui'].add(MainUi)
    mgr['Ui'].add(ImageUi)
    
   
    mgr['Ui'].init()
    mainUi =mgr['Ui'].new('Main',(tk,mgr))
    mainUi.init()
    mainUi.mainloop()

def test():
    mgr['Test']['List'].execute()
    mgr['Test']['Process'].execute()



if __name__ == '__main__':
    init()
    test()


