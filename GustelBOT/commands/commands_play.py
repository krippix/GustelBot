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
    
    #Makes Search all lowercase
    fullString = fullString.lower()
    
    #Removes spaces from filename and path
    fullString = fullString.replace(' ','')
        
    #Removes \ form filepath
    fullString = fullString.replace('\\','')
    
    
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
        
        #makes workingfile lowercase
        workingFile = fileNoExtension.lower()
        
        #Removes spaces from filename and path
        workingFile = workingFile.replace(' ','')
        
        #Removes \ form filepath
        workingFileWithFolder = workingFile.replace('\\','')
        

        #print(workingFileWithFolder)
        
        #Check Ration of file WITH Foldername
        
        print("vergleiche: "+workingFileWithFolder+" mit: "+fullString)
        ratio = SequenceMatcher(None,workingFileWithFolder,fullString).ratio()
        
        #Remove Folder from workingfile
        i = 1
        for char in workingFile:

            currentChar = workingFile[len(workingFile)-i]
            
            #Only keep String until first "\" appears
            if currentChar == '\\':
                workingFile = workingFile[len(workingFile)-i+1:]
                break

            #increment Current Char
            i = i + 1
        
        #print(workingFile)
        
        #Check ratio of file without Folder
        ratioNoFolder = SequenceMatcher(None,workingFile,fullString).ratio()
        
        #Put Ratio with file into list (Actual Filename)
        currentList = [ratio,ratioNoFolder,file]
        
        fileRatio.append(currentList)
    
    #Sort result by Ratio
    fileRatio.sort(reverse=True)
    
    
    resultPlus55 = []
    #Only include results with above 50%
    for result in fileRatio:
        if result[0] >= 0.55 or result[1] >= 0.55:
            resultPlus55.append(result)
            
    
    print(resultPlus55)
    
    #Calculates average of result with and without path
    
    
    #return most likely result (Filename of highest ratio, ratio)
    #TODO: Make a more specific decision
    print(fileRatio)
    
    
    if len(resultPlus55) == 0:
        return None
    
    else:
        #Check wich ratio was more likely
        if resultPlus55[0][0] >= resultPlus55[0][1]:
            finalRatio = resultPlus55[0][0]
        else:
            finalRatio = resultPlus55[0][1]
       
        
        
        return (resultPlus55[0][2],finalRatio)
    


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


def tree(basepath):
    
    itemlist = getAllFiles(basepath)
    
    treestring = ""
    
    for x in itemlist:
        treestring = treestring + str(x) + "\n"
    
    
    return treestring