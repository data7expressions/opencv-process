import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import queue as q
from os import path,getcwd,listdir



from ..core import *


class Ui(ChildManager):
    pass

class UiManager(Manager):
    def __init__(self):
        super(UiManager,self).__init__()
        self.icons = {}

    def add(self,value):
        value.set(self.mgr,self)
        key=Helper.rreplace(type(value).__name__, 'Ui', '')
        self.list[key]= value 

    def init(self):
        self.loadIcons()

    def loadIcons(self):
        iconsPath=path.join(getcwd(),'project/assets/icons')
        for item in listdir(iconsPath):
            name=path.splitext(path.basename(item))[0]
            self.icons[name] = tk.PhotoImage(file=path.join(iconsPath,item))  

    def getIcon(self,key):
        key = key.replace('.','')
        if key not in self.icons: key = '_blank'
        return self.icons[key.replace('.','')]


class MainUi(ttk.Frame,Ui):
    def __init__(self, tk):
        super().__init__(tk)
        self.tk= tk

    def init(self):
        self.layout()
        self.loadTree(self.mgr.context['workspace']) 
      

    def layout(self):
        name=path.basename(self.mgr.context['workspace'])
        self.tk.title(name)        
        self.treeview = ttk.Treeview(self)
        self.treeview.pack()
        self.pack()    

        # seguir ejemplo
        #https://recursospython.com/guias-y-manuales/vista-de-arbol-treeview-en-tkinter/

    
    def loadTree(self, _path, parent=""):
        for item in listdir(_path):            
            fullpath = path.join(_path,item)
            if path.isdir(fullpath):
                child = self.addItem(item,'folder',parent)                
                self.loadTree(fullpath,child)
            else:
                filename, file_extension = path.splitext(item)
                self.addItem(filename,file_extension,parent)  


    def addItem(self,name,icon, parent=""):        
        img=self.mgr['Ui'].getIcon(icon) 
        return self.treeview.insert(parent,tk.END,text=name, tags=("fstag",),image=img)