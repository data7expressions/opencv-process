from unittest import TestCase,main
from process.core import *
from mgr.base import Context
from os import path,getcwd

currentPath = path.dirname(path.realpath(__file__))
mgr = MainManager()
mgr.loadPlugin(path.join(currentPath,'data/base'))
mgr.loadPlugin(path.join(currentPath,'data/process'))


class TestProcess(TestCase):
    def test_simple(self):
        context = Context({"a":2,"b":5})
        processInstance = mgr.Process.create('bpm01',context)
        mgr.Process.start(processInstance,sync=True)
        self.assertEqual(context['a'],7)

def test():
    main()