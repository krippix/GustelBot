from difflib import SequenceMatcher
import os
import random





def chooseRandomFile(basepath):
    #chooses random File from basepath

    
    return random.choice(getAllFiles(basepath))

def searchFile(basepath,*args):
    #Searches files for closest match of parameters
    
    allFiles = getAllFiles(basepath)
    
    fullString = ""
    
    #Adds all arguments together, ignoring spaces
    for arg in args:
        fullString = fullString + arg
    
 
    
    fileRatio = []
    #Determines how close to the search the filenames are
    for file in allFiles:
        
        
        
        #Remove ending from file
        i = 1
        fileNoExtension = ""
        workingFile = ""
        for char in file:
            
            
            currentChar = file[len(file)-i]
            
            #Once first dot found, remove everything up until then from string
            if currentChar == '.':
                fileNoExtension = file[:len(file)-i]
                break

            #increment Current Char
            i = i + 1
        
        #Remove Spaces from String
        workingFile = fileNoExtension.replace(' ','')
        
        #Check Ration of file
        ratio = SequenceMatcher(None,workingFile,fullString).ratio()
        #print(file," -> ", ratio)
        
        #Put Ratio with file into tuple (Actual Filename)
        currentList = [ratio,file]
        
        fileRatio.append(currentList)
    
    #Sort result by Ratio
    fileRatio.sort()
    print(fileRatio)
    
    #return most likely result (Filename of highest ratio, ratio)
    #TODO: Make a more specific decision
    return((fileRatio[len(fileRatio)-1][1],(fileRatio[len(fileRatio)-1][0])))
    


def getAllFiles(basepath):
    
    includedFileTypes = [".wv",".wma",".webm",".wav",".vox",".voc",".tta",".sln",".rf64",".raw",".ra",".rm",".opus",".ogg",".oga",".mogg",".nmf",".msv",".mpc",".mp3",".mmf",".m4p",".m4b",".m4a",".ivs",".iklax",".gsm",".flac",".dvf",".dss",".dct",".cda",".awb",".au",".ape",".amr",".alac",".aiff",".act",".aax",".aac",".aa",".8svx",".3gp"]
    
    allFiles = []
    
    #Search Basedirectory For all files in folders and Subfolders
    for root, subdirs, files in os.walk(basepath):
        
        #remove basepath from result
        root = root[len(basepath):]
        
        #Search result list
        for file in files:
            
            #Check if current file contains allowed filetype
            for filetype in includedFileTypes:
                if file.lower().endswith(filetype):
                    if root != "":
                        allFiles.append(str(root+os.sep+file))
                
                    else:
                        allFiles.append(file)
    
    return allFiles