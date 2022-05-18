import logging, os, pathlib, random
from util import config

def get_files_rec(folder: pathlib.Path) -> list:
    # Returns list of tuples, format: (path, filename)
    foundFiles = []
    
    for triples in os.walk(folder):
        for file in triples[2]:
            foundFiles.append(({triples[0]}, file))

    return foundFiles


def get_random_file(folder: pathlib.Path) -> pathlib.Path:
    # returns random file from folder
    
    files = get_files_rec(folder)

    if not files:
        return None

    return random.choice(files)