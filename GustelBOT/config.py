#Python native
import configparser
from pathlib import Path

#Part of Project


#External


def checkini():
    #Checks if .ini File still exists
    return
    
def checkDataFolder():
    #Check if data folder exists and create if not
    try:
        Path("{}{}{}".format(Path(__file__).parent.parent, os.sep, "data")).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error("Failed to create data folder: "+str(e))
        logging.info("Exiting Program.")
        exit()
    return