
from tkinter import *
from .ui import *
from os import path,getcwd,listdir
#from mgr.core import *
# from mgr.process import *
from .core import *

mgr = MainManager() 
mgr.context={ 'workspace' : (path.join(getcwd(),'data/workspace')) }

def init():
   
   mgr.add(TypeManager)
   mgr.add(EnumManager)       
   mgr.add(TaskManager) 
   mgr.add(ExpressionManager) 
   mgr.add(ProcessManager) 
   mgr.add(TestManager)
   mgr.add(UiManager) 

   rootpath = getcwd()
   mgr.applyConfig(path.join(rootpath,'project/type.yaml'))

   mgr.loadPlugin(path.join(rootpath,'project/opencv'))
   mgr.loadPlugin(path.join(rootpath,'data/workspace'))


def ui():
    mgr['Ui'].add(MainUi)
    mgr['Ui'].add(ImageUi)
   
    mgr['Ui'].createSingleton('Main',{'master':Tk()})
    mgr['Ui']['Main'].init(path.join(getcwd(),'project/assets/icons'))
    mgr['Ui']['Main'].layout()
    mgr['Ui']['Main'].set(mgr.context['workspace'])
    mgr['Ui']['Main'].mainloop()    

def test():
    mgr['Test']['List'].execute()
    mgr['Test']['Process'].execute()

if __name__ == '__main__':
    init()
    test()
    ui()