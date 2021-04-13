
from tkinter import *
from os import path,getcwd
from py_mgr_tkinter.core import *
from base.init import initialize
from base.ui import *

def ui(mgr):

    mgr.Ui.add(MainUi)
    mgr.Ui.add(ContainerUi)
    mgr.Ui.add(FileImageUi)
    mgr.Ui.add(FileProcessUi)
    mgr.Ui.add(FileEditorUi)

    mgr.Ui.add(CvImageUi)
    mgr.Ui.add(EnumUi)
    mgr.Ui.add(NumberUi)
    mgr.Ui.add(DecimalUi)    
    mgr.Ui.add(StringUi) 
    mgr.Ui.add(FilepathUi) 
    mgr.Ui.add(PointUi)
    mgr.Ui.add(SizeUi) 
    mgr.Ui.add(RectangleUi)  
    
    tk=Tk()
    iconProvider = IconProvider(path.join(getcwd(), 'assets/icons'))
    mgr.addIconProvider(iconProvider)   
    main=mgr.Ui.singleton('Main',master=tk)
    main.set(path.join(getcwd(),'workspaces/example'))
    main.mainloop()    

if __name__ == '__main__':
    mgr=initialize()
    ui(mgr)
