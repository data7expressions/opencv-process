from process.core import entity
from ..core.entity import *

class CvtColor(FunctionEntity):
    def __init__(self):
        super(CvtColor,self).__init__()

main.el('Function').add(CvtColor())