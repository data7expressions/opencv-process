import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import queue as q
from os import path,getcwd,listdir
from PIL import ImageTk, Image
from ..core.base import *
from ..core.manager import * 
from ..core.uiTkinter import *


class TreeFilePanel(ttk.Frame):
    def __init__(self, master,mgr):
        super(TreeFilePanel,self).__init__(master)
        self.mgr=mgr
        self.onCommand=Event() 
        self.tree = ttk.Treeview(self)               
        self.tree.pack(expand=True,fill=tk.BOTH)
        self.rootPath=None        

    def set(self,rootPath):
        self.rootPath=rootPath
        name=path.basename(rootPath)
        self.tree.heading('#0', text=name)
        self.load(rootPath)

    def load(self, _path, parent=""):
        for item in listdir(_path):            
            fullpath = path.join(_path,item)
            if path.isdir(fullpath):
                child = self.addItem(fullpath,item,'folder',parent)                
                self.load(fullpath,child)
            else:
                filename, file_extension = path.splitext(item)
                self.addItem(fullpath,filename,file_extension,parent)

        # self.tree.bind("<Double-1>", self.onDoubleClick)
        self.tree.bind("<<TreeviewSelect>>", self.onSelect)              

    def addItem(self,fullpath,name,icon, parent=""):
        return self.tree.insert(parent,tk.END,iid=fullpath, text=name, tags=("cb"),image=self.mgr.getIcon(icon))

    def onSelect(self, event):        
        item = self.tree.selection()[0]
        if not path.isdir(item):
            self.onCommand(self,{'command':'select','data':item})          

    def subscribe(self,method): 
        self.onCommand += method 
          
    def unsubscribe(self,method): 
        self.onCommand -= method          

class TabsFilePanel(ttk.Frame):
    def __init__(self, master,mgr):
        super(TabsFilePanel,self).__init__(master)
        self.mgr=mgr
        self.onCommand=Event()
        self.frames= {}
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=True,fill=tk.BOTH)

    def set(self,fullpath):        
        name=path.basename(fullpath)
        frame ,tabIndex = self.getCurrent()
        frame.set(fullpath)
        self.tabs.tab(tabIndex, text=name)

    def getCurrent(self):
        frame=None
        tabIndex=None
        s=self.tabs.select()
        if s == '':
            frame = self.mgr['Ui'].new('Container',{'master':self.master})
            self.tabs.add(frame) 
            self.tabs.bind("<Button-1>", self.tab_switch)
            self.tabs.pack(expand = 1, fill ="both")
            tabIndex=self.tabs.index(self.tabs.select())
            self.frames[tabIndex] =  frame
        else:
            tabIndex=self.tabs.index(s)
            frame = self.frames[tabIndex]

        return frame ,tabIndex   

    def tab_switch(self,event):
        pass   

    def subscribe(self,method): 
        self.onCommand += method 
          
    def unsubscribe(self,method): 
        self.onCommand -= method       

class MainUi(ttk.Frame):
    def __init__(self,master,mgr): 
        super(MainUi,self).__init__(master)
        self.mgr= mgr
        self.init()
        self.layout()
  
    def init(self):          
        self.toolbar = ToolbarPanel(self,self.mgr)
        self.toolbar.load(self.config['Command']) 
        self.toolbar.subscribe(self.onCommand)      
        self.tree = TreeFilePanel(self,self.mgr)        
        self.tree.subscribe(self.onCommand)
        self.tabs = TabsFilePanel(self,self.mgr)
        self.tabs.subscribe(self.onCommand)
        self.pack(fill=tk.BOTH, expand=tk.YES)  

    def layout(self):
        #https://recursospython.com/guias-y-manuales/posicionar-elementos-en-tkinter/
          
        self.master.geometry("900x640")
        # UiHelper.center(self.master)
        tk.Grid.rowconfigure(self.master, 0, weight=1)
        tk.Grid.columnconfigure(self.master, 0, weight=1)        
        self.toolbar.grid(row=0, column=0,sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 0, weight=0)
        tk.Grid.columnconfigure(self, 0, weight=0)      
        self.tree.grid(row=1, column=0,sticky="nsew") 
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        self.tabs.grid(row=1, column=1,sticky="nsew") 
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=11)
        self.pack(fill=tk.BOTH, expand=tk.YES)         

    @property
    def config(self):    
        return self.mgr['Config']['Ui']['Main']     

    def set(self,workspacePath):
        name=path.basename(workspacePath)
        self.master.title(name)
        self.tree.load(workspacePath)  
  
    def onCommand(self,sender,args):
        print(args['command'])
    
        if args['command'] == 'select':
           self.tabs.set(args['data'])

        
    def onClose(self):
        row_id = self.tree.focus()
        print(row_id)

class ContainerUi(ttk.Frame):
    def __init__(self, master,mgr):
        super(ContainerUi,self).__init__(master)
        self.mgr=mgr
        self.frames = {}
        self.init()
        self.layout()        
        
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
        frame = self.mgr['Ui'].new(key,{'master':self})
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
        self.init()
        self.layout()       
        
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
        self.init()
        self.layout()       
        
    def init(self):
        self.panel = tk.Label(self)

    def layout(self):
        self.pack()   

    def set(self,fullpath):
        name, spec = self.getProcess(fullpath)
        img = self.createGraph(spec)
        self.showGraph(img)
    

    def getProcess(self,processPath):
        name=None
        spec=None        
        with open(processPath, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                if 'Process' in data:
                    l=data['Process']
                    name = list(l.keys())[0]
                    spec= l[name]                  
            except yaml.YAMLError as exc:
                print(exc)

        return name,spec         

    def createGraph(self,spec):
        pass
        # https://graphviz.readthedocs.io/en/stable/
        # https://graphviz.org/resources/
        # https://github.com/pydot/pydot

    def showGraph(self,imgPath):
        load = Image.open(imgPath)
        load = load.resize((640,480), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)
        self.panel.configure(image=img)    
        self.panel.image = img
        self.panel.place(x=0, y=0)
        self.panel.pack(expand = 1, fill ="both")




from pygments import lexers,highlight
from pygments.formatters import HtmlFormatter
# from tkhtmlview import HTMLLabel
from tkinterhtml import HtmlFrame
import re

class EditorUi(ttk.Frame):
    def __init__(self, master,mgr):
        super(EditorUi,self).__init__(master)
        self.mgr=mgr 
        self.htmlFrame=None
        self.init()
        self.layout()       
        
    def init(self):
        self.htmlFrame = HtmlFrame(self, horizontal_scrollbar="auto")
        # self.editor = tk.Text(self)
        # self.editor.mark_set("range_start", "1.0")

    def layout(self):
        self.pack()
        self.htmlFrame.pack()   

    def set(self,fullpath):
        file = open(fullpath, "r")
        data=file.read()
        list=lexers.get_all_lexers()
        lex = lexers.get_lexer_by_name("yaml")
        formatter = HtmlFormatter(full=True, style='monokai') 
        html=highlight(data, lex, formatter)
        result = re.sub(r'/[*][^*]*[*]+([^/*][^*]*[*]+)*/|//[^\n]*',r'', html)
        # html=html.replace('\n','')        
        self.htmlFrame.set_content(result)

        # html_label = HTMLLabel(self, html=html)
        # html_label.pack(fill="both", expand=True)
        # html_label.fit_height()

        # for token, content in lex(data, PythonLexer()):
        #     self.editor.mark_set("range_end", "range_start + %dc" % len(content))
        #     self.editor.tag_add(str(token), "range_start", "range_end")
        #     self.editor.mark_set("range_start", "range_end")

        # for token, content in lex(data, YamlLexer()):
        #     self.editor.mark_set("range_end", "range_start + %dc" %len(content))
        #     self.editor.tag_add(str(token), "range_start", "range_end")
        #     self.editor.mark_set("range_start", "range_end")
            # self.editor.tag_configure("Token.Text", foreground="black")
            # self.editor.tag_configure("Token.Literal.String.Single", foreground="red")
            # self.editor.tag_configure("Token.Literal.String.Double", foreground="green")
            # self.editor.tag_configure("Token.Literal.String.Doc", foreground="blue")





