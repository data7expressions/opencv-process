
from tkinter import *

from os import path,getcwd,listdir
#from mgr.core import *
# from mgr.process import *
from .core.base import *
from .core.manager import * 
from .core.uiTkinter import *
from .ui.main import *

rootpath = getcwd()

def init():   
   plugins= []
   plugins.append(path.join(rootpath,'project/main'))
   plugins.append(path.join(rootpath,'project/opencv'))
#    plugins.append(path.join(rootpath,'project/ui'))
   plugins.append(path.join(rootpath,'data/workspace'))

   mgr = MainManager()
   mgr.init(plugins) 
   mgr.context['workspace']=path.join(getcwd(),'data/workspace')

   return mgr

def ui(mgr):

    mgr.Ui.add(MainUi)
    mgr.Ui.add(ContainerUi)
    mgr.Ui.add(ImageUi)
    mgr.Ui.add(ProcessUi)
    mgr.Ui.add(EditorUi)

    mgr.applyConfig(path.join(rootpath,'project/ui/config.yaml'))
    

    tk=Tk()
    iconProvider= IconProvider(path.join(getcwd(),'project/assets/icons'))
    mgr.addIconProvider(iconProvider)
   
    main=mgr.Ui.singleton('Main',{'master':tk})
    main.set(mgr.context['workspace'])
    main.mainloop()    

def test(mgr):
    mgr.Test.List.execute()
    mgr.Test.Process.execute()

if __name__ == '__main__':
    mgr=init()
    # test(mgr)
    ui(mgr)