import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import queue as q
from os import path,getcwd,listdir
from PIL import ImageTk, Image


# from ..core import *




class MainUi(ttk.Frame):
    def __init__(self, tk,mgr):
        super().__init__(tk)
        self.mgr=mgr
        self.tk= tk

    def getIcon(self,icon):
        return self.mgr['Ui'].getIcon(icon)     
        

    def init(self):
        self.layout()
        self.tree_init()
        self.toolbar_init()
        #self.open() 
      

    def layout(self):
        name=path.basename(self.mgr.context['workspace'])
        self.tk.title(name)
        # self.tk.attributes('-fullscreen', True)
        pad=3
        self.tk.geometry("{0}x{1}+0+0".format(self.tk.winfo_screenwidth()-pad, self.tk.winfo_screenheight()-pad))
        self.tk.geometry('1024x768') 
        self.menu=tk.Menu(self.tk)
        # self.menu.pack(side=tk.TOP, fill=tk.BOTH)
        self.footer=ttk.Button(self.tk, text="footer")
        self.footer.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.tree = ttk.Treeview(self)
        self.tree.pack(side=tk.LEFT)
        self.tabs = ttk.Notebook(self.tk)
        self.tabs.pack(side=tk.RIGHT)
        self.tk.config(menu=self.menu)
        self.pack()    

        # seguir ejemplo
        #https://recursospython.com/guias-y-manuales/vista-de-arbol-treeview-en-tkinter/r


    def toolbar_init(self):
        
        self.menu.add_command(label="Open",image=self.getIcon('document-open'),command=self.onOpen)       
        self.menu.add_command(label="Close", image=self.getIcon('document-close'),command=self.onClose)
        # self.menu.add_cascade(label="File", menu=self.fileMenu)
        # self.menu.add(label="Save", menu=self.fileMenu)
        # toolbar = tk.Frame(self.tk, bd=1, relief=tk.RAISED)
    
    def onOpen(self):
        row_id = self.tree.focus()
        name=path.basename(row_id)
        f1 = self.mgr['Ui'].new('Image',(self.tabs,self.mgr))  
        self.tabs.add(f1, text= name)
        self.tabs.bind("<Button-1>", self.tab_switch)
        self.tabs.pack(expand = 1, fill ="both")
        f1.init(row_id) 
        print(row_id)

    def onClose(self):
        row_id = self.tree.focus()
        print(row_id)

    def tab_switch(self,event):
        pass
        # index = event.widget.index("@%d,%d" % (event.x, event.y))
        # title = event.widget.tab(index, "text")

    def tree_init(self):
        self.tree_load(self.mgr.context['workspace'])

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



class ImageUi(ttk.Frame):
    def __init__(self, master,mgr):
        ttk.Frame.__init__(self, master)
        self.mgr=mgr        
        self.pack()

    def init(self,fullpath):
        load = Image.open(fullpath)
        load = load.resize((640,480), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)        
        panel = tk.Label(self, image=img)
        panel.image = img
        panel.place(x=0, y=0)
        panel.pack(expand = 1, fill ="both")      

