
from tkinter import *
from .core import *
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

   rootpath = getcwd()
   mgr.applyConfig(path.join(rootpath,'project/type.yaml'))

   mgr.loadPlugin(path.join(rootpath,'project/opencv'))
   mgr.loadPlugin(path.join(rootpath,'project/process'))
   mgr.loadPlugin(path.join(rootpath,'data/workspace'))


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


