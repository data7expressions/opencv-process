
from tkinter import *
from os import path,getcwd,listdir
# from py_mgr.core import *
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
    main=mgr.Ui.singleton('Main',master=tk)
    main.set(path.join(getcwd(),'data/workspace'))
    main.mainloop()    

def test(mgr):
    mgr.Test.List.execute()
    # mgr.Test.Process.execute()

if __name__ == '__main__':
    mgr=initialize()
    ui(mgr)
