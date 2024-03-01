import logging, os, pathlib, random
from util import config
from difflib import SequenceMatcher


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


def get_random_file(folder: pathlib.Path) -> pathlib.Path:
    '''Returns random file from folder'''
    
    files = get_files_rec(folder)

    if not files:
        return None

    return random.choice(files)


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