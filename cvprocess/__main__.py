
from .ui.main import MainUi
from tkinter import *
from .application import *
from .process.managers import *
from .test.process import *



def main():
    base = Tk()
    mainManager = MainManager() 
    mainUi = MainUi(base,mainManager)       
    application = Aplication(mainUi,mainManager)
    application.init()
    base.mainloop()

def test():
    mainManager = MainManager() 
    testProcess = TestProcess(mainManager)
    testProcess.execute()

test()