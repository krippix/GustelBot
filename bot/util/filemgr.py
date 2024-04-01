# default
import logging
import os
import pathlib
import random
from difflib import SequenceMatcher
# pip
import mutagen
# internal
from util import config


def get_files_rec(folder: pathlib.Path) -> list[pathlib.Path]:
    '''Returns list of tuples, format: (path, filename)'''
    if folder.is_file():
        logging.error("File instead of folder provided!")
        return []
    found_files = []  
    for file in folder.iterdir():
        if file.is_file():
            found_files.append(file)
            continue
        if file.is_dir():
            found_files += get_files_rec(file)
    return found_files


def get_random_file(folder: pathlib.Path, maxlen: int) -> pathlib.Path:
    """Returns random file from folder, if maxlen is 0 ignore maxlen
    """
    files = get_files_rec(folder)
    files_clean = []
    for file in files:
        try:
            soundlen = mutagen.File(file).info.length
            if maxlen == 0 or soundlen <= maxlen and soundlen != 0:
                files_clean.append(file)
        except Exception:
            logging.warning(f"No length found for {file}")
            continue
    if not files_clean:
        return None
    return random.choice(files_clean)


def get_folders(path: pathlib.Path) -> list[pathlib.Path]:
    folder_list = []
    for item in path.iterdir():
        if item.is_dir():
            folder_list.append(item)
    return folder_list


def search_files(lst: list[pathlib.Path], keyword: str, threshhold = 0.65) -> pathlib.Path | None:
    result_list = []
    for item in lst:
        ratio = SequenceMatcher(None, item.name.lower(), keyword.lower()).ratio()
        if ratio >= threshhold:
            result_list.append((item, ratio))
    result_list.sort(key = lambda x:x[1], reverse = True)
    if len(result_list) == 0:
        return None
    return result_list[0][0]