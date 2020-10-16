#Python "native"
import logging
from pathlib import Path
import os

#Part of Project
import config


#external
from discord.ext import commands


#File locations
iniFile = "{}{}{}".format(Path(__file__).parent.parent, os.sep,"config.ini")
dataFolder = Path("{}{}{}".format(Path(__file__).parent.parent, os.sep, "data"))





def main():
    
    #Check requirements / create missing files
    config.checkDataFolder(dataFolder)
    config.checkini(iniFile)
    
    
    
    
    
    return 