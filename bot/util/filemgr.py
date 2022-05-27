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


def get_file_names(folder: pathlib.Path) -> list:
    '''Returns list of filenames. WITHOUT path information'''
    found_files = get_files_rec(folder)
    file_names = []

    for file in found_files:
        file_names.append(f"{pathlib.Path(file[1]).with_suffix('')}")
    
    file_names.sort()
    return file_names


def get_random_file(folder: pathlib.Path) -> pathlib.Path:
    '''Returns random file from folder'''
    
    files = get_files_rec(folder)

    if not files:
        return None

    return random.choice(files)