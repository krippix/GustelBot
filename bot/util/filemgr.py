import logging, os, pathlib, random
from util import config

def get_files_rec(folder: pathlib.Path) -> list:
    '''Returns list of tuples, format: (path, filename)'''
    foundFiles = []
    
    for triple in os.walk(folder):        
        for file in triple[2]:
            foundFiles.append((triple[0], file))

    foundFiles.sort()

    return foundFiles


def get_random_file(folder: pathlib.Path) -> pathlib.Path:
    '''returns random file from folder'''
    
    files = get_files_rec(folder)

    if not files:
        return None

    return random.choice(files)