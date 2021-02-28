import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import queue as q
from os import path,getcwd,listdir
from PIL import ImageTk, Image
from .core import *

class MainUi(ttk.Frame):
    def __init__(self,master,mgr): 
        super(MainUi,self).__init__(master)
        self.mgr= mgr
        self.icons = {}
        
    
    def loadIcons(self,iconsPath):
        for item in listdir(iconsPath):
            name=path.splitext(path.basename(item))[0]
            self.icons[name] = tk.PhotoImage(file=path.join(iconsPath,item))  

    def getIcon(self,key):
        key = key.replace('.','')
        if key not in self.icons: key = '_blank'
        return self.icons[key.replace('.','')]         
  
    def init(self,iconsPath):
        self.loadIcons(iconsPath)
        self.menu=tk.Menu(self.master)
        self.master.config(menu=self.menu)
        self.footer=ttk.Button(self.master, text="footer")
        self.tree = ttk.Treeview(self)
        self.tabs = ttk.Notebook(self.master)        
        self.toolbar_init()
        

    def toolbar_init(self):        
        self.menu.add_command(label="Open",image=self.getIcon('document-open'),command=self.onOpen)       
        self.menu.add_command(label="Close", image=self.getIcon('document-close'),command=self.onClose)
        # self.menu.add_cascade(label="File", menu=self.fileMenu)
        # self.menu.add(label="Save", menu=self.fileMenu)
        # toolbar = tk.Frame(self.master, bd=1, relief=tk.RAISED)      
  
    def layout(self):
         # self.master.attributes('-fullscreen', True)
        pad=3
        self.master.geometry("{0}x{1}+0+0".format(self.master.winfo_screenwidth()-pad, self.master.winfo_screenheight()-pad))
        self.master.geometry('1024x768') 
        self.footer.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.tree.pack(side=tk.LEFT)
        self.tabs.pack(side=tk.RIGHT)
        self.pack()         

        # seguir ejemplo
        #https://recursospython.com/guias-y-manuales/vista-de-arbol-treeview-en-tkinter/r

    def set(self,workspacePath):
        name=path.basename(workspacePath)
        self.master.title(name)
        self.tree_load(workspacePath)
        

   


    def onOpen(self):
        fullpath = self.tree.focus()
        name=path.basename(fullpath) 

        s=self.tabs.select()
        if s == None:
            frame = self.mgr['Ui'].create('Container',{'master':self.master})
            self.tabs.add(frame, text= name) 
            self.tabs.bind("<Button-1>", self.tab_switch)
            self.tabs.pack(expand = 1, fill ="both")
            frame.set(fullpath) 
        else:
            index=self.tabs.index(s)
        
    def onClose(self):
        row_id = self.tree.focus()
        print(row_id)

    def tab_switch(self,event):
        pass
        # index = event.widget.index("@%d,%d" % (event.x, event.y))
        # title = event.widget.tab(index, "text")

    def tree_load(self, _path, parent=""):
        for item in listdir(_path):            
            fullpath = path.join(_path,item)
            if path.isdir(fullpath):
                child = self.tree_addItem(fullpath,item,'folder',parent)                
                self.tree_load(fullpath,child)
            else:
                filename, file_extension = path.splitext(item)
                self.tree_addItem(fullpath,filename,file_extension,parent) 

    def tree_addItem(self,fullpath,name,icon, parent=""):
        return self.tree.insert(parent,tk.END,iid=fullpath, text=name, tags=("cb"),image=self.getIcon(icon))

    # def open(self):
        
    #     f1 = ImageFrame(self.tabs, "Tab1")

    #     self.tabs.add(f1, text= "Tab1")
    #     self.tabs.bind("<Button-1>", self.tab_switch)
    #     self.tabs.pack(expand = 1, fill ="both") 

       
    # def tab_switch(self,event):
    #     index = event.widget.index("@%d,%d" % (event.x, event.y))
    #     title = event.widget.tab(index, "text")


class ContainerUi(ttk.Frame):
    def __init__(self, master,mgr):
        super(ImageUi,self).__init__(master)
        self.mgr=mgr
        self.frames = {}        
        
    def init(self):
        pass

    def layout(self):
        self.pack() 

    def getFrame(self,key):        
        if key in self.frames:
            return self.frames[key] 
        frame = self.mgr['Ui'].create(key,{'master':self.master})
        frame.init()
        frame.layout()
        self.frames[key] = frame
        return frame      

    def set(self,fullpath):
        key= 'Image'
        frame=self.getFrame(key) 
        frame.set(fullpath) 
        print(fullpath)        

class ImageUi(ttk.Frame):
    def __init__(self, master,mgr):
        super(ImageUi,self).__init__(master)
        self.mgr=mgr        
        
    def init(self):
        pass

    def layout(self):
        self.pack()   

    def set(self,fullpath):
        load = Image.open(fullpath)
        load = load.resize((640,480), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)        
        panel = tk.Label(self, image=img)
        panel.image = img
        panel.place(x=0, y=0)
        panel.pack(expand = 1, fill ="both")      

