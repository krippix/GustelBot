# default
import hashlib
import logging
import pathlib
import random
import shutil
from difflib import SequenceMatcher
# pip
import mutagen
# internal


def get_files_rec(folder: pathlib.Path) -> list[pathlib.Path]:
    """
    Returns list of tuples, format: (path, filename)
    """
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


def get_random_file(folder: pathlib.Path, max_len: int) -> pathlib.Path:
    """
    Returns random file from folder, if max_len is 0 ignore max_len
    """
    files = get_files_rec(folder)
    files_clean = []
    for file in files:
        sound_len = get_sound_length(file)
        if sound_len and max_len == 0 or sound_len <= max_len:
            files_clean.append(file)
    return random.choice(files_clean)


def get_sound_length(file: pathlib.Path) -> int | None:
    """
    Retrieves the length of a sound file
    """
    try:
        return mutagen.File(file).info.length
    except AttributeError:
        return None


def get_folders(path: pathlib.Path) -> list[pathlib.Path]:
    folder_list = []
    for item in path.iterdir():
        if item.is_dir():
            folder_list.append(item)
    return folder_list


def search_files(lst: list[pathlib.Path], keyword: str, threshhold=0.65) -> pathlib.Path | None:
    result_list = []
    for item in lst:
        ratio = SequenceMatcher(None, item.name.lower(), keyword.lower()).ratio()
        if ratio >= threshhold:
            result_list.append((item, ratio))
    result_list.sort(key=lambda x: x[1], reverse=True)
    if len(result_list) == 0:
        return None
    return result_list[0][0]


def is_audio_file(file: pathlib.Path) -> bool:
    """
    Checks if provided file is an audio file.
    """
    if file := mutagen.File(file) is None:
        return False
    if file.info.length is not None and file.info.length > 0:
        return True
    return False


def calculate_md5(file: pathlib.Path) -> str:
    """
    Calculates MD5 hash of provided file.
    """
    hash_md5 = hashlib.md5()
    buffer_size = 65536
    with open(file, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            hash_md5.update(data)
    return hash_md5.hexdigest()


def move_to_folder(file: pathlib.Path, folder: pathlib.Path):
    """
    moves sound file to sound folder to be used by the bot.
    """
    if not file.is_file():
        raise FileNotFoundError
    if not folder.is_dir():
        raise NotADirectoryError
    shutil.move(file, f'{folder}/{file.name}')
