from process.core import MainManager
from os import path,getcwd

def onChange(key,value,oldValue=None):
    print(key+' value: '+str(value))


if __name__ == "__main__":
    mgr = MainManager()

    rootpath = getcwd()
    mgr.loadPlugin(path.join(rootpath,'plugins/opencv'))
    # mgr.loadPlugin(path.join(rootpath,'data/workspace'))
    mgr.applyConfig(path.join(rootpath,'data/workspace/test/cvtColor.yml'))

    print(mgr.Enum.getEnum('ColorConversion'))
    print(mgr.Config.Task['CvtColor']['input'])

    init = {'source':'/home/flavio/develop/opencv-process/data/workspace/data/source.jpg'
            ,'target':'/home/flavio/develop/opencv-process/data/workspace/data/target.jpg'}
                  
                 
    process = mgr.Process.create('test',init)
    process.context.onChange += onChange
    mgr.Process.start(process) 


     