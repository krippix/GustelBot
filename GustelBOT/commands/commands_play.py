import os
import random





def chooseRandomFile(basepath, *exclude):
    #Chooses Random File out of Folder and ALL SUBFOLDERS
    
    allFiles = []    
    
    for root, subdirs, files in os.walk(basepath):
        
        #remove basepath from result
        #TODO Doesent work on windows server WTF?
        root = root[len(basepath):]
        
        for x in files:
            
            #Ignore Filetypes
            if not x.lower().endswith(exclude):
                if root != "":
                    allFiles.append(str(root+os.sep+x))
                
                else:
                    allFiles.append(x)
                
        
    return random.choice(allFiles)