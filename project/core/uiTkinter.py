from .base import *
import tkinter as tk
from tkinter import ttk
from os import path,listdir

class UiMediatior(Mediator):
    def __init__(self):
        super(UiMediatior, self).__init__()
        self._currentEditor=None

    @property
    def currentEditor(self):
        return self._currentEditor

    @currentEditor.setter
    def currentEditor(self,value):
        self._currentEditor=value  

class UiHelper():

    @staticmethod
    def center(win):
        # Center the root screen
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify() 

class ToolTip():
    def __init__(self, widget):
        self.widget = widget
        self.tipWindow = None
        self.id = None
        self.x = self.y = 0
    
    def showtip(self, text):
        self.text = text
        if self.tipWindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox('insert')
        x = x + self.widget.winfo_rootx() + 0
        y = y + cy + self.widget.winfo_rooty() + 40
        self.tipWindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry('+%d+%d' % (x, y))
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background='#000000', foreground='yellow', relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)
     
    def hidetip(self):
        tw = self.tipWindow
        self.tipWindow = None
        if tw:
            tw.destroy()
    
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

class Frame(ttk.Frame):
    def __init__(self, master, mgr,mediator):
        super(Frame, self).__init__(master)
        self.mgr = mgr
        self.mediator=mediator
        self.mediator.onCommand+=self.onCommand
        self.init()
        self.layout()
        
    def __del__(self):
        self.mediator.onCommand-=self.onCommand
        self.master.destroy()      

    def init(self):
        pass

    def layout(self):
        pass

    def onCommand(self,sender,command,args):
        pass

    

class ToolbarPanel(Frame):
    def __init__(self, master,mgr,mediator):        
        super(ToolbarPanel,self).__init__(master,mgr,mediator)        

    def init(self):
        self.buttons = {}

    def load(self,dic):
        for key in dic:
            item=Helper.nvl(dic[key],{})
            item['command'] = key
            self.add(**item)

    def add(self,command,img=None,tootip=None):
        icon = self.mgr.getIcon(Helper.nvl(img,command))
        btn = ttk.Button(self, image=icon, command=  lambda: self.mediator.raiseCommand(command,{}) )
        btn.image = icon
        btn.pack(side=tk.LEFT)
        self.createToolTip(btn,Helper.nvl(tootip,command))
        self.buttons[command] =btn

    def createToolTip(self, widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)        
       
class TreeFilePanel(Frame):
    def __init__(self, master, mgr,mediator):        
        super(TreeFilePanel, self).__init__(master,mgr,mediator)

    def init(self):
        self.rootPath = None
        self.tree = ttk.Treeview(self)
    def layout(self):
        self.tree.pack(expand=True, fill=tk.BOTH)      

    def set(self, rootPath):
        self.rootPath = rootPath
        name = path.basename(rootPath)
        self.tree.heading('#0', text=name)
        self.load(rootPath)

    def load(self, _path, parent=""):
        for item in listdir(_path):
            fullpath = path.join(_path, item)
            if path.isdir(fullpath):
                child = self.addItem(fullpath, item, 'folder', parent)
                self.load(fullpath, child)
            else:
                filename, file_extension = path.splitext(item)
                self.addItem(fullpath, filename, file_extension, parent)

        # self.tree.bind("<Double-1>", self.onDoubleClick)
        self.tree.bind("<<TreeviewSelect>>", self.onSelect)      

    def addItem(self, fullpath, name, icon, parent=""):
        return self.tree.insert(parent, tk.END, iid=fullpath, text=name, tags=("cb"), image=self.mgr.getIcon(icon))

    def onSelect(self, event):
        item = self.tree.selection()[0]
        if not path.isdir(item):
            self.mediator.raiseCommand(self,'select',{'item': item})

class TabsFilePanel(Frame):
    def __init__(self, master, mgr,mediator):
        super(TabsFilePanel, self).__init__(master,mgr,mediator)        

    def init(self):
        self.frames = {}
        self.tabs = ttk.Notebook(self)

    def layout(self):
        self.tabs.pack(expand=True, fill=tk.BOTH)

    def onCommand(self,sender,command,args):
        if command == 'select':
            self.set(args['item'])

    def set(self, fullpath):
        name = path.basename(fullpath)
        frame, tabIndex = self.getCurrent()
        frame.set(fullpath)
        # frame.current()
        self.tabs.tab(tabIndex, text=name)

    def getCurrent(self):
        frame = None
        tabIndex = None
        s = self.tabs.select()
        if s == '':
            frame = self.mgr['Ui'].new('Container', {'master': self.master,'mediator': self.mediator})
            self.tabs.add(frame)
            self.tabs.bind("<Button-1>", self.tab_switch)
            self.tabs.pack(expand=1, fill="both")
            tabIndex = self.tabs.index(self.tabs.select())
            self.frames[tabIndex] = frame
        else:
            tabIndex = self.tabs.index(s)
            frame = self.frames[tabIndex]

        return frame, tabIndex

    def tab_switch(self, event):
        pass

  