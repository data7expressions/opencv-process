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
    def __init__(self, master, mgr):
        super(MainUi, self).__init__(master,mgr,UiMediatior())

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
    def __init__(self, master, mgr,mediator):
        super(TabsFilePanel, self).__init__(master,mgr,mediator)        

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
            frame = self.mgr.Ui.new('Container', {'master': self.master,'mediator': self.mediator})
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
    def __init__(self, master, mgr,mediator):        
        super(ContainerUi, self).__init__(master, mgr,mediator) 

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
        self.currentEditor = self.mgr.Ui.new(key, {'master': self,'mediator':self.mediator})
        return self.currentEditor

class FileEditor(Frame):
    def __init__(self, master, mgr,mediator):        
        super(FileEditor, self).__init__(master, mgr,mediator)
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

class ImageUi(FileEditor):
    def __init__(self, master, mgr,mediator):
        super(ImageUi, self).__init__(master, mgr,mediator)

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

class ProcessGraphPanel(Frame):
    def __init__(self, master,mgr,mediator):
        super(ProcessGraphPanel,self).__init__(master, mgr,mediator)
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
        load = Image.open(imgPath)
        load = load.resize((640, 480), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(load)
        self.panel.configure(image=img)
        self.panel.image = img
        self.panel.place(x=0, y=0)
        self.panel.pack(expand=1, fill="both")

class ControlsPanel(Frame):
    def __init__(self, master,mgr,mediator):
        super(ControlsPanel,self).__init__(master, mgr,mediator)

    def init(self):
        self.controls=[]
 
    def set(self, vars):
        self.initControls(vars)
        self.layoutControls()

    def initControls(self,vars):        
        for name in vars:
            var = vars[name]
            control={'var':var
                    ,'label': tk.Label(self, text =name, font = "50") 
                    ,'control': self.createControl(self,var['type'])
                    }
            self.controls.append(control)
            
    def layoutControls(self):        
        for i,p in enumerate(self.controls):            
            p['label'].place(relx=0, y=(i+1)*40,relwidth=0.4, height=30)
            p['control'].place(relx=0.5, y=(i+1)*40, relwidth=0.5, height=30)
        # self.pack(fill=tk.BOTH, expand=tk.YES)                      

    def createControl(self,master,type):
        if type == 'number':
            from_=None
            to= None
            if type['sign'] ==  True:
                to = (type['precision'] * 8)/2
                from_ = (to-1)*-1 
            else:
                to = type['precision'] * 8
                from_ = 0                                   
            return tk.Spinbox(master, from_= from_, to = to)
        elif type.startswith('Enum.'):
            enum=type.replace('Enum.','')
            values= []
            for k in self.mgr.Enum[enum].values.keys():
                values.append(k) 
            return ttk.Combobox(master,values=values)
            # ver como seleccionar el valor de acuerdo al item seleccionado en el combo
            # https://stackoverflow.com/questions/54283975/python-tkinter-combobox-and-dictionary
        else:
            return tk.Label(master,text=type)               

#  https://realpython.com/python-descriptors/
class ImageCtl(tk.Label):
    def __init__(self, master=None, cnf={}, **kw):
        super(ImageCtl,self).__init__(master, cnf,**kw)

    @property
    def value(self):
        return self.image
    @value.setter
    def value(self,value):
        _image = Image.fromarray(value)
        _image = _image.resize((self.winfo_width(), self.winfo_height()), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(_image)
        self.configure(image=image)
        self.image = image

class ImagesPanel(Frame):
    def __init__(self, master,mgr,mediator):
        super(ImagesPanel,self).__init__(master, mgr,mediator)

    def init(self):
        self._controls={}

    def set(self, vars):
        self.initControls(vars)
        self.layoutControls()        

    def initControls(self,vars):        
        for name in vars:
            self._controls[name] = ImageCtl(self,text =name,width=160,height=120)
            
    def layoutControls(self):
        i=0
        for key in self._controls:
            self._controls[key].place(x=(160*i)+20, y=0, width=160, height=120)
            i=i+1
        # for i,p in enumerate(self.controls):
        #     p['control'].place(x=(160*i)+20, y=0, width=160, height=120)

    def changeValue(self,key,value):
        if key in self._controls:
            self._controls[key].value =value    

class ProcessUi(FileEditor):
    def __init__(self, master, mgr,mediator):
        super(ProcessUi, self).__init__(master, mgr,mediator)

    def init(self):
        self.graph = ProcessGraphPanel(self,self.mgr,self.mediator)
        self.controlsPanel = ControlsPanel(self,self.mgr,self.mediator)
        self.imagesPanel = ImagesPanel(self,self.mgr,self.mediator)
        self.spec = None
        self.processInstance = None

    def layout(self):
        tk.Grid.rowconfigure(self, 0, weight=3)
        tk.Grid.columnconfigure(self, 0, weight=3)        
        self.graph.grid(row=0, column=0, sticky="nsew")
        tk.Grid.rowconfigure(self, 0, weight=3)
        tk.Grid.columnconfigure(self, 1, weight=1)
        self.controlsPanel.grid(row=0, column=1, sticky="nsew")
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        self.imagesPanel.grid(row=1, column=0, sticky="nsew")
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def set(self, fullpath):
        self.spec = self.getProcess(fullpath)
        self.images = dict(filter(lambda p: p[1]['bind'] == True and p[1]['type']=='image', self.spec['vars'].items()))
        self.controls = dict(filter(lambda p: p[1]['bind'] == True and p[1]['type']!='image', self.spec['vars'].items()))
        self.graph.set(self.spec)
        self.imagesPanel.set(self.images)
        self.controlsPanel.set(self.controls)

    def onMessage(self,sender,verb,resource,args): 
        if self.current == False:
            return
        if resource == 'process' and self.spec != None:
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
        context = {'source':'/home/flavio/develop/opencv-process/data/workspace/data/source.jpg'
                  ,'target':'/home/flavio/develop/opencv-process/data/workspace/data/target.jpg'
                  }
        self.processInstance = self.mgr.Process.create(self.spec['name'],context)
        self.processInstance.context.onChange += self.process_context_onChange 
        self.mgr.Process.start(self.processInstance.id)        

     

    def process_stop(self):
        if self.processInstance != None:
           self.mgr.Process.stop(self.processInstance.id) 
    def process_pause(self):
        if self.processInstance != None:
           self.mgr.Process.pause(self.processInstance.id) 

    def process_context_onChange(self,key,value,oldValue):
        if key in self.images:
            self.imagesPanel.changeValue(key,value)     

class EditorUi(FileEditor):
    def __init__(self, master, mgr,mediator):
        super(EditorUi, self).__init__(master, mgr,mediator)

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
