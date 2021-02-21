from .process.core import *
from .process.managers import *
from .opencv.tasks import *
import os
import yaml

main = MainManager() 

def addManager(manager):

    main.add(manager)  

def applyConfig(configPath):
    with open(configPath, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            for key in data:
                main.get(key).loadConfig(data[key])
        except yaml.YAMLError as exc:
            print(exc)

def get(key):
    return main.get(key)


addManager(TypeManager())
addManager(EnumManager())       
addManager(TaskManager()) 
addManager(NodeManager()) 
addManager(ProcessManager()) 

get('Node').add(StartNode())
get('Node').add(EndNode())
get('Node').add(TaskNode())

get('Task').add(CvtColor())


rootpath = os.getcwd()
applyConfig(os.path.join(rootpath,'cvlab','config/core.yaml'))
applyConfig(os.path.join(rootpath,'cvlab','config/opencv.yaml'))
applyConfig(os.path.join(rootpath,'cvlab','config/process.yaml'))

print(get('Enum').get('ColorConversionCodes').values)
print(get('Task').get('CvtColor').params)