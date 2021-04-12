
from os import path,getcwd,listdir
from py_expression.core import Exp
from py_expression_opencv.lib import *
from py_mgr.core import MainManager
# from py_mgr_tkinter.core import IconProvider
from .core import *
import tkinter as tk


class IconProvider():
    def __init__(self,iconsPath=None): 
        self.icons = {}
        if iconsPath is not None:
           self.loadIcons(iconsPath)

    def loadIcons(self,iconsPath):
        for item in listdir(iconsPath):
            name=path.splitext(path.basename(item))[0]
            self.icons[name] = tk.PhotoImage(file=path.join(iconsPath,item))  

    def getIcon(self,key):
        key = key.replace('.','')
        if key not in self.icons: key = '_blank'
        return self.icons[key.replace('.','')] 


def initialize():
    
    exp = Exp()
    loadOpenCvExpressions(exp)
       
    mgr = MainManager()
    mgr.add(EnumManager)
    mgr.add(ProcessManager)
    iconProvider = IconProvider(path.join(getcwd(), 'assets/icons'))
    mgr.addIconProvider(iconProvider)

    dir_path = path.dirname(path.realpath(__file__))
    mgr.applyConfig(path.join(dir_path,'config.yaml'))   

    mgr.loadPlugin(path.join(getcwd(),'data/workspace')) 

    return mgr;
