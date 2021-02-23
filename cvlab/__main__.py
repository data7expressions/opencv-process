
from .ui.main import MainUi
from tkinter import *
from .application import *
from .process.managers import *



def main():
    base = Tk()
    mainManager = MainManager() 
    mainUi = MainUi(base,mainManager)       
    application = Aplication(mainUi,mainManager)
    application.init()
    base.mainloop()

main()