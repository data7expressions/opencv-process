import unittest
from tkinter import *
from os import path, getcwd, listdir
# from py_mgr.core import *
from py_mgr_tkinter.core import *
from base.init import initialize
from base.ui import *

mgr = None


class TestManager(unittest.TestCase):
    def test_enumManager(self):
        colorConversion = mgr.Enum.getEnum('ColorConversion')
        self.assertEqual(colorConversion['BGR2GRAY'], 6)

    def test_configProcess(self):
        mgr.loadPlugin(path.join(getcwd(), 'workspaces/test'))

        processSpec = mgr.Process.getSpec('test')
        self.assertEqual(processSpec.kind, 'bpm')

    def test_executeProcess(self):

        def onChange(key,value,oldValue):
            print('change: '+key)
            print(value)

        context = Context({'workspace': 'workspaces/test','source': 'data/source.jpg', 'target': 'data/target.jpg'})
        context.onChange += onChange
        instance = mgr.Process.create('test', context)
        mgr.Process.start(instance, sync=True)
        self.assertEqual(context['finished'], 'yes')        

g
if __name__ == '__main__':
    mgr = initialize()
    unittest.main()
