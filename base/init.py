
from os import path,getcwd,listdir
from .py_expression import Exp
# from py_expression.core import Exp
from py_expression_opencv.lib import *
# from py_mgr.core import MainManager
from .mgr import MainManager
from .core import *

def initialize():
    
    exp = Exp()
    loadOpenCvExpressions(exp)
       
    mgr = MainManager()
    mgr.add(EnumManager)
    mgr.add(ProcessManager)

    dir_path = path.dirname(path.realpath(__file__))
    # mgr.loadPlugin(path.join(dir_path,'main'))      
    mgr.applyConfig(path.join(dir_path,'config.yaml'))    

    return mgr;
