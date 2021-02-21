from .process.core import *
from .process.managers import *
from .opencv.tasks import *
import yaml

main = Main() 

def addManager(manager):
    main.add(manager)  

def applyConfig(configPath):
    with open(configPath, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            for key in data:
                main.el(key).loadConfig(data[key])
        except yaml.YAMLError as exc:
            print(exc)

def get(key):
    return main.el(key)


addManager(Type())
addManager(Enum())       
addManager(Function()) 
addManager(Activity())    
addManager(Process()) 

get('Function').add(CvtColor)

applyConfig('config/main.yaml')

print(get('Enum').el('ColorConversionCodes').values)
print(get('Function').el('CvtColor').parameters)