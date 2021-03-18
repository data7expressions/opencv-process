from typing import Text
from pygments import lexers, highlight
import re
from tkinterhtml import HtmlFrame
from pygments.formatters import HtmlFormatter
from graphviz import Digraph
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import queue as q
from os import path, getcwd, listdir
from PIL import ImageTk, Image
from ..core.base import *
from ..core.manager import *
from ..core.uiTkinter import *


class MainUi(Frame):
    def __init__(self, master, mgr,**kw):
        super(MainUi, self).__init__(master,mgr,UiMediatior(),**kw)

    def init(self):
        self.toolbar = ToolbarPanel(self, self.mgr,self.mediator)               
        self.tree = TreeFilePanel(self, self.mgr,self.mediator)        
        self.tabs = TabsFilePanel(self, self.mgr,self.mediator)
        self.toolbar.load(self.config['Commands'])

    @property
    def config(self):
        return self.mgr.Config.Ui['Main']    

    def layout(self):
        # https://recursospython.com/guias-y-manuales/posicionar-elementos-en-tkinter/

        self.master.geometry("1800x800")
        # UiHelper.center(self.master)
        tk.Grid.rowconfigure(self, 0, weight=0)
        tk.Grid.columnconfigure(self, 0, weight=0)
        self.toolbar.grid(row=0, column=0, sticky="nsew")
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        self.tree.grid(row=1, column=0, sticky="nsew")
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=11)
        self.tabs.grid(row=1, column=1, sticky="nsew")        
        self.pack(fill=tk.BOTH, expand=tk.YES)   

    def set(self, workspacePath):
        name = path.basename(workspacePath)
        self.master.title(name)
        self.tree.load(workspacePath)

    def onMessage(self,sender,verb,resource,args):       
        print(verb)

    def onClose(self):
        row_id = self.tree.focus()
        print(row_id)

class TabsFilePanel(Frame):
    def __init__(self, master, mgr,mediator,**kw):
        super(TabsFilePanel, self).__init__(master,mgr,mediator,**kw)        

    def init(self):
        self.frames = {}
        self.tabs = ttk.Notebook(self)

    def layout(self):
        self.tabs.pack(expand=True, fill=tk.BOTH)

    def onMessage(self,sender,verb,resource,args):
        if verb == 'select' and resource == 'file':
            self.set(args['item'])

    def set(self, fullpath):
        name = path.basename(fullpath)
        frame, index = self.getCurrent()
        frame.set(fullpath)
        self.tabs.tab(index, text=name)
        self.setCurrent(index)

    def setCurrent(self,index):
        for k in self.frames:
            self.frames[k].current  = k == index

    def tab_switch(self, event):
        print(event)

    def getCurrent(self):
        frame = None
        tabIndex = None
        s = self.tabs.select()
        if s == '':
            frame = self.mgr.Ui.new('Container', master=self.master,mediator=self.mediator)
            self.tabs.add(frame)
            self.tabs.bind("<Button-1>", self.tab_switch)
            self.tabs.pack(expand=1, fill="both")
            tabIndex = self.tabs.index(self.tabs.select())
            self.frames[tabIndex] = frame
        else:
            tabIndex = self.tabs.index(s)
            frame = self.frames[tabIndex]

        return frame, tabIndex

class ContainerUi(Frame):
    def __init__(self, master, mgr,mediator,**kw):        
        super(ContainerUi, self).__init__(master, mgr,mediator,**kw) 

    def init(self):
        self.currentEditor = None

    @property
    def current(self):
        return self.currentEditor.current if self.currentEditor != None else False

    @current.setter
    def current(self,value):
        if self.currentEditor != None:
            self.currentEditor.current = value
            if value :                               
                commands = self.currentEditor.config['Commands'] if 'Commands' in self.currentEditor.config else {} 
                if commands != None:
                    self.mediator.send(self,'add','command',{'commands':commands,'contextual': True})

    def set(self, fullpath):
        editor  = self.getEditor(fullpath)
        editor.set(fullpath)         

    def getEditor(self, fullpath):
        file = path.basename(fullpath)
        filename, fileExtension = path.splitext(file)
        fileExtension = fileExtension.replace('.', '')
        key = None
        for key in self.mgr.Config.Ui:
            extensions = self.mgr.Config.Ui[key]['extensions']
            if fileExtension in extensions:
                break
        if key == None:
            key = 'Editor'

        if self.currentEditor != None:
            currentKey = self.mgr.Ui.key(self.currentEditor)
            if key == currentKey:
                return self.currentEditor
            else:
                self.currentEditor.destroy()      
        self.currentEditor = self.mgr.Ui.new(key, master=self,mediator=self.mediator)
        return self.currentEditor

class FileEditor(Frame):
    def __init__(self, master, mgr,mediator,**kw):        
        super(FileEditor, self).__init__(master, mgr,mediator,**kw)
        self._current= False

    @property
    def config(self):
        key = self.mgr.Ui.key(self)
        return self.mgr.Config.Ui[key]

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self,value):
        self._current=value      

class FileImageUi(FileEditor):
    def __init__(self, master, mgr,mediator,**kw):
        super(FileImageUi, self).__init__(master, mgr,mediator,**kw)

    def init(self):
        self.panel = tk.Label(self)

    def layout(self):
        self.pack() 

    def set(self, fullpath):
        load = Image.open(fullpath)
        load = load.resize((640, 480), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)
        self.panel.configure(image=img)
        self.panel.image = img
        self.panel.place(x=0, y=0)
        self.panel.pack(expand=1, fill="both")

class ProcessDiagramPanel(Frame):
    def __init__(self, master,mgr,mediator,**kw):
        super(ProcessDiagramPanel,self).__init__(master, mgr,mediator,**kw)
    """
    References: 
        https://graphviz.readthedocs.io/en/stable/examples.html
        https://graphviz.readthedocs.io/en/stable/
        https://graphviz.org/resources/
        https://github.com/pydot/pydot
        https://graphviz.org/doc/info/shapes.html
    """
    def init(self):
        self.panel = tk.Label(self)
    def layout(self):
        self.pack()


    def set(self, spec):
        img = self.createGraph(spec)
        self.showGraph(img)
   
    def createGraph(self,spec):
        filename = path.join('temp', spec['name'])
        f = Digraph(comment='The Round Table', filename=filename,engine='neato', format="png")

        try:
            nodes = spec['nodes']
            starts = dict(filter(lambda p: p[1]['type'] == 'Start', nodes.items()))
            for name in starts:
                f.attr('node', shape='circle')
                f.node(name, name)

            tasks = dict(filter(lambda p: p[1]['type'] == 'Task', nodes.items()))
            for name in tasks:
                task = tasks[name]

                str_input = ''
                for p in task['input']:
                    sep = '' if str_input == '' else ','
                    str_input = str_input+sep+p['name']+':'+p['exp']

                str_output = ''
                for p in task['output']:
                    sep = '' if str_output == '' else ','
                    str_output = str_output+sep+p['assig']

                label = ''
                if str_output == '':
                    label = task['task']+'('+str_input+')'
                else:
                    label = str_output+'='+task['task']+'('+str_input+')'

                f.attr('node', shape='box')
                f.node(name, label)

            ends = dict(filter(lambda p: p[1]['type'] == 'End', nodes.items()))
            for name in ends:
                f.attr('node', shape='doublecircle')
                f.node(name, name)

            for source in nodes:
                node = nodes[source]
                transition = node['transition']
                for p in transition:
                    f.edge(source,p['target'])
        except Exception as ex:
            print(ex)
        f.render()
        return filename+'.png'

    def showGraph(self, imgPath):
        self.update_idletasks()
        h = self.winfo_height()
        w = self.winfo_width()
        load = Image.open(imgPath)
        load = load.resize((w, h), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)
        self.panel.configure(image=img)
        self.panel.image = img
        self.panel.place(x=0, y=0)
        self.panel.pack(expand=1, fill="both")

class Control(ttk.Frame):
    def __init__(self,type,var,varName,mgr,master=None,**kw):
        super(Control, self).__init__(master,**kw)
        self.mgr = mgr
        self._type = type
        self._var = var
        self._varName = varName

    def onChanged(self, event=None):
        self.event_generate('<<Changed>>')

    @property
    def type(self):
        return self._type
    @property
    def var(self):
        return self._var
    @property
    def varName(self):
        return self._varName         
 
class NumberUi(Control):
    def __init__(self,type,var,varName,mgr=None,master=None,**kw):
        super(NumberUi, self).__init__(type,var,varName,mgr,master,**kw)
        self.var = tk.IntVar()

        from_,to=mgr.Type.range(type)   
        
        self.lbl = tk.Label(self,text=varName)        
        self.sbox = tk.Spinbox(self, from_= from_, to = to, textvariable=self.var,command=self.onChanged)      
        
        self.lbl.place(relx=0, y=0,relwidth=0.4, height=25)
        self.sbox.place(relx=0.5, y=0, relwidth=0.5, height=25)
        self.pack()

    def get(self):                              
        return self.var.get()

    def set(self,value):
        self.var.set(value)

class StringUi(Control):
    def __init__(self,type,var,varName,mgr=None,master=None,**kw):
        super(StringUi, self).__init__(type,var,varName,mgr,master,**kw)
        self.bindVar = tk.StringVar()
        self.bindVar.trace("w", lambda name, index, mode, sv=self.bindVar: self.onChanged())         
        
        self.lbl = tk.Label(self,text=varName)        
        self.txt = tk.Entry(self,textvariable=self.bindVar)      
        
        self.lbl.place(relx=0, y=0,relwidth=0.4, height=25)
        self.txt.place(relx=0.5, y=0, relwidth=0.5, height=25)
        self.pack()

    def get(self):                              
        return self.bindVar.get()

    def set(self,value):
        self.bindVar.set(value)

class FilePathUi(Control):
    def __init__(self,type,var,varName,mgr=None,master=None,**kw):
        super(FilePathUi, self).__init__(type,var,varName,mgr,master,**kw)
        self.bindVar = tk.StringVar()
        self.bindVar.trace("w", lambda name, index, mode, sv=self.bindVar: self.onChanged())
        
        self.lbl = tk.Label(self,text=varName)        
        self.txt = ttk.Entry(self,textvariable=self.bindVar)
        self.btn = ttk.Button(self,text='...',command=self.openFilename )       
        
        self.lbl.place(relx=0, y=0,relwidth=0.3, height=25)
        self.txt.place(relx=0.3, y=0, relwidth=0.5, height=25)
        self.btn.place(relx=0.8, y=0, relwidth=0.2, height=25)
        self.pack()

    def openFilename(self):
        current =self.bindVar.get()
        initialdir=path.dirname(path.abspath(current))
        result = fd.askopenfilename(initialdir=initialdir)
        if not result:return
        self.set(result)

    def get(self):                              
        return self.bindVar.get()

    def set(self,value):
        self.bindVar.set(value)

class EnumUi(Control):
    def __init__(self,type,var,varName,mgr=None,master=None,**kw):
        super(EnumUi, self).__init__(type,var,varName,mgr,master,**kw)
        enumName=var['type'].replace('Enum.','')
        self.enum= self.mgr.Enum[enumName]
        
        self.lbl = tk.Label(self,text=varName)        
        self.cmb = ttk.Combobox(self,values=sorted(self.enum.values.keys()))       
        self.cmb.bind('<<ComboboxSelected>>',self.onChanged)

        self.lbl.place(relx=0, y=0,relwidth=0.4, height=25)
        self.cmb.place(relx=0.5, y=0, relwidth=0.5, height=25)
        self.pack()        

    def get(self):                              
        return self.enum.values[self.get_key()]

    def get_key(self):
        return self.cmb.get()

    def set(self,value):
        key=None 
        for k in self.enum.values: 
            if self.enum.values[k]== value:
                key=k
                break
        if key != None:
           self.cmb.set(key)    

class PointUi(Control):
    def __init__(self,type:dict,var:dict,varName:str,mgr=None,master=None,**kw):
        super(PointUi, self).__init__(type,var,varName,mgr,master,**kw)
        self.varX = tk.IntVar()
        self.varY = tk.IntVar()

        xType = self.mgr.Type['int']
        from_,to=mgr.Type.range(xType) 
        
        self.xlbl = tk.Label(self,text='x')        
        self.xSbox = tk.Spinbox(self, from_= from_, to = to, textvariable=self.varX,command=self.onChanged)
        self.ylbl = tk.Label(self,text='x')        
        self.ySbox = tk.Spinbox(self, from_= from_, to = to, textvariable=self.varY,command=self.onChanged)       
        
        self.xlbl.place(relx=0, y=0,relwidth=0.1, height=25)
        self.xSbox.place(relx=0.5, y=0, relwidth=0.3, height=25)
        self.ylbl.place(relx=0, y=0,relwidth=0.1, height=25)
        self.ySbox.place(relx=0.5, y=0, relwidth=0.3, height=25)
        self.pack()

    def get(self)->Point:                              
        return Point(self.varX.get(),self.varY.get())

    def set(self,value:Point):
        self.varX.set(value.x)
        self.varY.set(value.y)

class SizeUi(Control):
    def __init__(self,type:dict,var:dict,varName:str,mgr=None,master=None,**kw):
        super(SizeUi, self).__init__(type,var,varName,mgr,master,**kw)
        self.varW = tk.IntVar()
        self.varH = tk.IntVar()
        
        wType = self.mgr.Type['int']
        from_,to=mgr.Type.range(wType) 
        
        self.wlbl = tk.Label(self,text='w')        
        self.wSbox = tk.Spinbox(self, from_= from_, to = to, textvariable=self.varW,command=self.onChanged)
        self.hlbl = tk.Label(self,text='h')        
        self.hSbox = tk.Spinbox(self, from_= from_, to = to, textvariable=self.varH,command=self.onChanged)       
        
        self.wlbl.place(relx=0, y=0,relwidth=0.1, height=25)
        self.wSbox.place(relx=0.5, y=0, relwidth=0.3, height=25)
        self.hlbl.place(relx=0, y=0,relwidth=0.1, height=25)
        self.hSbox.place(relx=0.5, y=0, relwidth=0.3, height=25)
        self.pack()

    def get(self)->Size:                              
        return Size(self.varW.get(),self.varH.get())

    def set(self,value:Size):
        self.varW.set(value.w)
        self.varH.set(value.h)

#  https://realpython.com/python-descriptors/
class CvImageUi(Control):
    def __init__(self,type,var,varName,mgr=None,master=None, **kw):
        super(CvImageUi, self).__init__(type,var,varName,mgr,master,**kw)
               
        self.lblTitle = tk.Label(self,height=1,bg="blue")
        self.lblTitle.pack(fill='x')
        self.lblTitle.config(text=varName)        

        self.lblImage = tk.Label(self,bg="black")        
        self.lblImage.pack(fill='both', expand=1)
        self.pack()
   
    def get(self): 
        return self.lblImage.image
    def set(self,value):    
        _image = Image.fromarray(value)
        _image = _image.resize((self.lblImage.winfo_width(), self.lblImage.winfo_height()), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(_image)
        self.lblImage.configure(image=image)
        self.lblImage.image = image

class ControlsPanel(Frame):
    def __init__(self, master,mgr,mediator,title=None,**kw):
        self.title = title 
        super(ControlsPanel,self).__init__(master, mgr,mediator,**kw)
        self._onChange=Event()
               

    @property
    def onChange(self):
        return self._onChange
    @onChange.setter
    def onChange(self,value):
        self._onChange=value 

    def init(self):
        self._controls={}
        if self.title:  
            self.lblTitle = tk.Label(self,text=self.title,anchor='w', bg='#000', fg='#fff',padx=1) 

    def layout(self):
        if self.title:
            self.lblTitle.place(relx=0,y=0,relwidth=1, height=20)

    def set(self, vars):
        self.initControls(vars)
        self.layoutControls() 

    def initControls(self,vars):        
        for name in vars:
            control = self.createControl(name,vars[name])
            control.bind('<<Changed>>', self.controlOnChanged)
            self._controls[name]= control

    def layoutControls(self):
        i=0
        titleHeight =  21 if self.title else 1 
        for name in self._controls:
            self._controls[name].place(relx=0,y=(i*30)+titleHeight,relwidth=1, height=30)
            i=i+1                    

    def createControl(self,key,var):
        typeName = 'enum' if var['type'].startswith('Enum.') else var['type']
        type = self.mgr.Type[typeName]
        control= self.mgr.Ui.new(type['ctl'],type=type,var=var,varName=key,mgr=self.mgr,master=self)
        if 'initValue' in var:
            control.set(var['initValue'])
        return control        

    def controlOnChanged(self, event):
        value = event.widget.get()
        key = event.widget.varName
        self._onChange(key,value) 

    def contextOnChange(self,name,value):
        if name in self._controls:
            self._controls[name].set(value)

class GrapthPanel(ControlsPanel):
    def __init__(self, master,mgr,mediator,title=None,**kw):
        super(GrapthPanel,self).__init__(master, mgr,mediator,title,**kw)
            
    def layoutControls(self):  
        titleHeight =  21 if self.title else 1      
        self.update_idletasks()
        h = self.winfo_height() - titleHeight
        w =  int(h * 1.33)
        i=0
        for name in self._controls:
            self._controls[name].place(x=((w+1)*i)+2, y=titleHeight, width=w, height=h)
            i=i+1

class FileProcessUi(FileEditor):
    def __init__(self, master, mgr,mediator,**kw):
        super(FileProcessUi, self).__init__(master, mgr,mediator,**kw)

    def init(self):
        self.diagram = ProcessDiagramPanel(self,self.mgr,self.mediator)
        self.inputVarsPanel = ControlsPanel(self,self.mgr,self.mediator,title='input')
        self.processVarsPanel = ControlsPanel(self,self.mgr,self.mediator,title='bind vars')
        self.grapthVarsPanel = GrapthPanel(self,self.mgr,self.mediator,title='bind grapth')
        self.processInstance = None

    def layout(self):
        self.diagram.place(relx=0, rely=0,relwidth=0.75, relheight=0.75)
        self.diagram.configure(background='red')
        self.inputVarsPanel.place(relx=0.75, rely=0,relwidth=0.25, relheight=0.25)
        self.inputVarsPanel.configure(background='yellow')
        self.processVarsPanel.place(relx=0.75, rely=0.25,relwidth=0.25, relheight=0.75)
        self.processVarsPanel.configure(background='blue')
        self.grapthVarsPanel.place(relx=0, rely=0.75,relwidth=0.75, relheight=0.25)
        self.grapthVarsPanel.configure(background='pink')
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def set(self, fullpath):       

        context = {'source':'/home/flavio/develop/opencv-process/data/workspace/data/source.jpg'
                  ,'target':'/home/flavio/develop/opencv-process/data/workspace/data/target.jpg'
                  }
        spec = self.getProcess(fullpath)          
        self.processInstance = self.mgr.Process.apply(spec['name'],spec,context)

        vars = self.processInstance.spec['vars']
        context = self.processInstance.context
        for p in vars:
            if p in context:
                vars[p]['initValue'] = context[p]

        self.inputVars = dict(filter(lambda p: p[1]['isInput']== True, vars.items()))
        self.processVars = dict(filter(lambda p: p[1]['bind'] == True and p[1]['isInput']== False and p[1]['type']!='cvImage',vars.items()))
        self.grapthVars = dict(filter(lambda p: p[1]['bind'] == True and p[1]['isInput']== False and p[1]['type']=='cvImage', vars.items()))
        self.diagram.set(self.processInstance.spec)
        
        self.inputVarsPanel.set(self.inputVars)
        self.processVarsPanel.set(self.processVars)
        self.grapthVarsPanel.set(self.grapthVars)        

        context.onChange += self.process_context_onChange
        self.inputVarsPanel.onChange+= self.control_onChange
        self.processVarsPanel.onChange+= self.control_onChange
        self.grapthVarsPanel.onChange+= self.control_onChange
        

    def onMessage(self,sender,verb,resource,args): 
        if self.current == False:
            return
        if resource == 'process' and self.processInstance.spec != None:
            if verb == 'start':
                self.process_start()
            elif verb == 'stop':
                self.process_stop()
            elif verb == 'pause':
                self.process_pause()         

    def getProcess(self, processPath):
        name = None
        spec = None
        with open(processPath, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                if 'Process' in data:
                    l = data['Process']
                    name = list(l.keys())[0]
                    spec = l[name]
            except yaml.YAMLError as ex:
                print(ex)
            except Exception as ex:
                print(ex)    

        self.mgr.Process.completeSpec(name,spec)
        return spec

    def process_start(self):
        self.mgr.Process.start(self.processInstance)
    def process_stop(self):
        if self.processInstance != None and self.processInstance.id != None:
           self.mgr.Process.stop(self.processInstance.id) 
    def process_pause(self):
        if self.processInstance != None and self.processInstance.id != None:
           self.mgr.Process.pause(self.processInstance.id)

    def control_onChange(self,key,value):
        self.processInstance.context[key]=value

    def process_context_onChange(self,key,value,oldValue):
        if key in self.grapthVars:
            self.grapthVarsPanel.contextOnChange(key,value)
        elif key in self.processVars:
            self.processVarsPanel.contextOnChange(key,value)          

class FileEditorUi(FileEditor):
    def __init__(self, master, mgr,mediator,**kw):
        super(FileEditorUi, self).__init__(master, mgr,mediator,**kw)

    def init(self):
        self.htmlFrame = HtmlFrame(self, horizontal_scrollbar="auto")
        # self.editor = tk.Text(self)
        # self.editor.mark_set("range_start", "1.0")

    def layout(self):
        self.pack()
        self.htmlFrame.pack()

    def set(self, fullpath):
        file = open(fullpath, "r")
        data = file.read()
        list = lexers.get_all_lexers()
        lex = lexers.get_lexer_by_name("yaml")
        formatter = HtmlFormatter(full=True, style='monokai')
        html = highlight(data, lex, formatter)
        result = re.sub(r'/[*][^*]*[*]+([^/*][^*]*[*]+)*/|//[^\n]*', r'', html)
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
