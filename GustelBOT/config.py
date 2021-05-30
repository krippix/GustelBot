#Python native
import configparser
import logging
import os
from pathlib import Path

#Part of Project


#External


#inifile
def inifile():
    return "{}{}{}{}{}".format(Path(__file__).parent.parent, os.sep, "data", os.sep,"config.ini")

def dataFolder():
    return Path("{}{}{}".format(Path(__file__).parent.parent, os.sep, "data"))

def soundFolder():
    if readini("BOTCONFIG","soundfilefolder") == "":
        #logging.info("No Path for audiofiles set. Using GustelBOT/data/soundfiles/")
        return Path(dataFolder(),"soundfiles")
    else:
        return readini("BOTCONFIG", "soundfilefolder")  

def youtubeFolder():
    return "{}{}{}{}{}".format(Path(__file__).parent.parent, os.sep, "data", os.sep,"youtube")

def getVersion():
    return "v0.0.1"


def checkLocations():
    #Check folder/files after startup
    logging.info("config.ini location: "+str(inifile()))
    checkini()
    logging.info("data folder location: "+str(dataFolder()))
    checkFolder(dataFolder())
    logging.info("sound folder location: "+str(soundFolder()))
    checkFolder(soundFolder())
     


def checkini():
    #Checks if .ini File exists
    logging.info("Checking if: "+inifile()+" exists...")
    
    if Path(inifile()).exists():    
        logging.info("config.ini found!")
        return True
    
    else:
        logging.warning("config.ini not found!")
        
        logging.info("Attempting to create config.ini")
        try:
            open(inifile(), "x")
            logging.info("config.ini created!")
        except Exception as e:
            logging.error("Failed to create config.ini: "+str(e))
            logging.info("Exiting Program.")
            exit()
        
        #Once the file is created, create default ini Structure
   
        config = configparser.ConfigParser()
        
        config.add_section("BOTCONFIG")
        config.set("BOTCONFIG","prefix","&")
        config.set("BOTCONFIG","language","en")
        config.set("BOTCONFIG","soundfileFolder","")
        
        config.add_section("DISCORD")
        config.set("DISCORD","token","")
        
        config.add_section("REDDIT")
        config.set("REDDIT","clientID","")
        config.set("REDDIT","clientSecret","")
        config.set("REDDIT","creatorUsername","")
        
        config.add_section("YOUTUBE")
        config.set("YOUTUBE","clientID","")
        config.set("YOUTUBE","clientSecret","")
        
        cfgfile = open(inifile(),'w')
        config.write(cfgfile)
        
        #TODO: Create config file with predefined settings
        
    return False



def checkFolder(currentFolder):
    #Check if data folder exists and create if not
    
    try:
        currentFolder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error("Failed to create data folder: "+str(e))
        logging.info("Exiting Program.")
        exit()
    return



def readini(section, option):
    #Returns chosen section and name
    
    parse = configparser.ConfigParser()
    
    logging.debug("Parsing Section: "+section+", name: "+option+" from: "+inifile())
    
    try:
        parse.read(inifile())
    except Exception as e:
        logging.warning(str(e))
    
    try:
        return parse.get(section, option)
    except Exception as e:
        logging.error(str(e))
    

    
    
    
    
    