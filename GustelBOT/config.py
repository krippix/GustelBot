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


def checkini(inilocation):
    #Checks if .ini File exists
    
    if Path(inilocation).exists():
        print(inilocation)
        logging.info("config.ini exists!")
    else:
        logging.warning("config.ini not found!")
        
        logging.info("Attempting to create config.ini")
        try:
            open(inilocation, "x")
            logging.info("config.ini created!")
        except Exception as e:
            logging.error("Failed to create config.ini: "+str(e))
            logging.info("Exiting Program.")
            exit()
        
        #Once the file is created, create default ini Structure
        config = configparser.ConfigParser()
        config.read(inilocation)
        config['DEFAULT']['path'] = '/var/shared/'    # update
        config['DEFAULT']['default_message'] = 'Hey! help me!!'   # create

        with open('FILE.INI', 'w') as configfile:    # save
            config.write(configfile)
        
        #TODO: Create config file with predefined settings
        
    return
