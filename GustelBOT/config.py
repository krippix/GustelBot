#Python native
import configparser
import logging
from pathlib import Path

#Part of Project


#External



def checkDataFolder(folderlocation):
    #Check if data folder exists and create if not
    try:
        folderlocation.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error("Failed to create data folder: "+str(e))
        logging.info("Exiting Program.")
        exit()
    return


def checkini(configini):
    #Checks if .ini File exists
    
    
    logging.info("Checking if: "+configini+" exists...")
    
    if Path(configini).exists():
        
        logging.info("config.ini found!")
    else:
        logging.warning("config.ini not found!")
        
        logging.info("Attempting to create config.ini")
        try:
            open(configini, "x")
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
        config.set("DISCORD","token","1234567890")
        
        cfgfile = open(configini,'w')
        config.write(cfgfile)
        
        #TODO: Create config file with predefined settings
        
    return

def readini(inifile, section, option):
    #Returns chosen section and name
    
    parse = configparser.ConfigParser()
    
    logging.debug("Parsing Section: "+section+", name: "+option+" from: "+inifile)
    
    try:
        parse.read(inifile)
    except Exception as e:
        logging.warning(str(e))
    
    try:
        return parse.get(section, option)
    except Exception as e:
        logging.error(str(e))
    

    
    
    
    
    