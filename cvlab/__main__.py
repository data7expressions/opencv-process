from .process.core import *
from .process.managers import *
from .opencv.tasks import *
import os
import yaml

main = MainManager() 


def applyConfig(configPath):
    with open(configPath, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            for key in data:
                main.get(key).loadConfig(data[key])
        except yaml.YAMLError as exc:
            print(exc)


main.add(TypeManager())
main.add(EnumManager())       
main.add(TaskManager()) 
# main.add(NodeManager()) 
main.add(ProcessManager()) 

# get('Node').add(StartNode())
# get('Node').add(EndNode())
# get('Node').add(TaskNode())

main.get('Task').add(Cv_CvtColor())
main.get('Task').add(Cv_ImRead())


rootpath = os.getcwd()
applyConfig(os.path.join(rootpath,'cvlab','config/core.yaml'))
applyConfig(os.path.join(rootpath,'cvlab','config/opencv.yaml'))
applyConfig(os.path.join(rootpath,'cvlab','config/process.yaml'))

print(main.manager('Enum','Cv_ColorConversionCodes').values)
print(main.manager('Task','Cv_CvtColor').params)

context = {'vars':{}}
main.manager('Process','test').start(context)