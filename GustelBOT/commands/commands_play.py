import os
import random





def chooseRandomFile(basepath):
    #Chooses Random File out of Folder and ALL SUBFOLDERS
    
    allFiles = []    
    
    for root, subdirs, files in os.walk(basepath):
        
        #remove basepath from result
        root = root[len(basepath):]
        
        
        
        for x in files:
            
            if root != "":
                allFiles.append(root+os.sep+x)
            else:
                allFiles.append(x)
        
    
    return random.choice(allFiles)