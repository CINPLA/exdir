from enum import Enum
import os
import pathlib
from . import exdir_object as exob

VALID_CHARACTERS = ("abcdefghijklmnopqrstuvwxyz1234567890_-.")


class NamingRule(Enum):
    SIMPLE = 1
    STRICT = 2
    THOROUGH = 3
    NONE = 4


def minimal(parent_path, name):
    path = parent_path / name
    name_str = str(name)

    if len(name_str) < 1:
        raise NameError("Name cannot be empty.")

    reserved_names = [exob.META_FILENAME,
                      exob.ATTRIBUTES_FILENAME,
                      exob.RAW_FOLDER_NAME]

    dosnames = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3",
                "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6",
                "LPT7", "LPT8", "LPT9"]

    if name_str in reserved_names:
        raise NameError("Name cannot be '" + name_str + "' because it is a reserved filename in Exdir.")

    if name_str in dosnames:
        raise NameError("Name cannot be '" + name_str + "' because it is a reserved filename in Windows.")


def strict(parent_path, name):
    minimal(parent_path, name)
    path = parent_path / name
    name_str = str(name)

    for char in name_str:
        if char not in VALID_CHARACTERS:
            raise NameError("Name '" + name_str + "' contains invalid character '" + char + "'.\n" +
                            "Valid characters are:\n" + VALID_CHARACTERS)

    if os.path.exists(path):
        raise FileExistsError("Filename '" + name_str + "' already exsits in '" + str(path) + "'")


def thorough(parent_path, name):
    minimal(parent_path, name)
    path = parent_path / name
    name_str = str(name)

    for char in name_str:
        if char.lower() not in VALID_CHARACTERS:
            raise NameError("Name contains invalid character '" + char + "'.\n" +
                            "Valid characters are:\n" + VALID_CHARACTERS)

        for item in os.listdir(parent_path):
            if name_str.lower() == item.lower():
                raise FileExistsError("A directory with name (case independent) '" + name_str +
                                "' already exists and cannot be made according " +
                                "to the naming rule 'thorough'.")

    if os.path.exists(path):
        raise FileExistsError("Filename '" + name_str + "' already exsits in '" + str(path) + "'")


def none(parent_path, name):
    pass
