import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import queue as q
import os

class MainUi(ttk.Frame):
    def __init__(self, base,manager):
        self.base= base
        self.manager=manager
        self.context= { 'workspace' : (os.path.join(os.getcwd(),'workspace/process.yaml')) }
        super().__init__(base)

    def init(self):
        self.layout()
        self.loadTree()   

    def layout(self):
        self.base.title("Vista de árbol en Tkinter")        
        self.treeview = ttk.Treeview(self)
        self.treeview.pack()
        self.pack()    

    def loadTree(self):
        item = self.treeview.insert("", tk.END, text="Elemento 1")
        self.treeview.insert(item, tk.END, text="Subelemento 1")

        # seguir ejemplo
        #https://recursospython.com/guias-y-manuales/vista-de-arbol-treeview-en-tkinter/

    