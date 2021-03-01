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
        self.frames= {}
        
    
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
        

   
    def getCurrent(self):
        frame=None
        tabIndex=None
        s=self.tabs.select()
        if s == '':
            frame = self.mgr['Ui'].create('Container',{'master':self.master})
            self.tabs.add(frame) 
            self.tabs.bind("<Button-1>", self.tab_switch)
            self.tabs.pack(expand = 1, fill ="both")
            tabIndex=self.tabs.index(self.tabs.select())
            self.frames[tabIndex] =  frame
        else:
            tabIndex=self.tabs.index(s)
            frame = self.frames[tabIndex]

        return frame ,tabIndex   

    def onOpen(self):
        fullpath = self.tree.focus()
        name=path.basename(fullpath)
        frame ,tabIndex = self.getCurrent()
        frame.set(fullpath)
        self.tabs.tab(tabIndex, text=name) 

        
        
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
        super(ContainerUi,self).__init__(master)
        self.mgr=mgr
        self.frames = {}        
        
    def init(self):
        pass

    def layout(self):
        self.pack() 

    def getFrame(self,fullpath):

        file= path.basename(fullpath)
        filename, fileExtension = path.splitext(file)
        fileExtension = fileExtension.replace('.','')
        key=None
        for key in self.mgr['Config']['Ui']:
           extensions= self.mgr['Config']['Ui'][key]['extensions']
           if fileExtension in extensions:
               break
        if key == None: key = 'Editor'
        
        if key in self.frames:
            return self.frames[key] 
        frame = self.mgr['Ui'].create(key,{'master':self})
        frame.init()
        frame.layout()
        self.frames[key] = frame
        return frame      

    def set(self,fullpath):
        frame=self.getFrame(fullpath) 
        frame.set(fullpath) 
        print(fullpath)        

class ImageUi(ttk.Frame):
    def __init__(self, master,mgr):
        super(ImageUi,self).__init__(master)
        self.mgr=mgr 
        self.panel=None       
        
    def init(self):
        self.panel = tk.Label(self)

    def layout(self):
        self.pack()   

    def set(self,fullpath):
        load = Image.open(fullpath)
        load = load.resize((640,480), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)
        self.panel.configure(image=img)    
        self.panel.image = img
        self.panel.place(x=0, y=0)
        self.panel.pack(expand = 1, fill ="both")  

class ProcessUi(ttk.Frame):
    def __init__(self, master,mgr):
        super(ProcessUi,self).__init__(master)
        self.mgr=mgr 
        self.panel=None       
        
    def init(self):
        pass

    def layout(self):
        self.pack()   

    def set(self,fullpath):
        pass

from pygments import lex
from pygments.lexers import PythonLexer,YamlLexer

class EditorUi(ttk.Frame):
    def __init__(self, master,mgr):
        super(EditorUi,self).__init__(master)
        self.mgr=mgr 
        self.editor=None       
        
    def init(self):
        self.editor = tk.Text(self)
        self.editor.mark_set("range_start", "1.0")

    def layout(self):
        self.pack()
        self.editor.pack()   

    def set(self,fullpath):
        file = open(fullpath, "r")
        data=file.read()

        for token, content in lex(data, PythonLexer()):
            self.editor.mark_set("range_end", "range_start + %dc" % len(content))
            self.editor.tag_add(str(token), "range_start", "range_end")
            self.editor.mark_set("range_start", "range_end")

        # for token, content in lex(data, YamlLexer()):
        #     self.editor.mark_set("range_end", "range_start + %dc" %len(content))
        #     self.editor.tag_add(str(token), "range_start", "range_end")
        #     self.editor.mark_set("range_start", "range_end")
            # self.editor.tag_configure("Token.Text", foreground="black")
            # self.editor.tag_configure("Token.Literal.String.Single", foreground="red")
            # self.editor.tag_configure("Token.Literal.String.Double", foreground="green")
            # self.editor.tag_configure("Token.Literal.String.Doc", foreground="blue")

        