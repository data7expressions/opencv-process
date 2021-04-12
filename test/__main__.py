import unittest
from tkinter import *
from os import path,getcwd,listdir
# from py_mgr.core import *
from py_mgr_tkinter.core import *
from base.init import initialize
from base.ui import *

mgr=None

class TestManager(unittest.TestCase):
    def test_enumManager(self):  
        colorConversion= mgr.Enum.getEnum('ColorConversion')      
        self.assertEqual(colorConversion['BGR2GRAY'],6)

    def test_processManager(self):
        processSpec= mgr.Process.getSpec('test')
        self.assertEqual(processSpec.kind,'bpm')

if __name__ == '__main__':
    mgr=initialize()
    unittest.main()



# class ProcessTest():
#     def __init__(self,mgr):
#         self.mgr= mgr    
#     def execute(self):


#         init = {'source':'/home/flavio/develop/opencv-process/data/workspace/data/source.jpg'
#                ,'target':'/home/flavio/develop/opencv-process/data/workspace/data/target.jpg'
#                }
                  
                 
#         process = self.mgr.Process.create('test',init)
#         process.context.onChange += self.onChange
#         self.mgr.Process.start(process.id) 


#     def onChange(self,key,value,oldValue):
#         print(key+' value: '+str(value)) 