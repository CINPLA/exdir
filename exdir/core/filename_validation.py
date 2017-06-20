from enum import Enum
import os
from . import exdir_object as exob

VALID_CHARACTERS = ("abcdefghijklmnopqrstuvwxyz1234567890_-.")

class NamingRule(Enum):
    SIMPLE = 1
    STRICT = 2
    THOROUGH = 3
    NONE = 4


def minimal(path, name):
    if len(name) < 1:
        raise NameError("Name cannot be empty.")

    reserved_names = [exob.META_FILENAME,
                      exob.ATTRIBUTES_FILENAME,
                      exob.RAW_FOLDER_NAME]

    dosnames = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3",
                "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6",
                "LPT7", "LPT8", "LPT9"]

    if name in reserved_names:
        raise NameError("Name cannot be '" + name + "' because it is a reserved filename in Exdir.")

    if name in dosnames:
        raise NameError("Name cannot be '" + name + "' because it is a reserved filename in Windows.")

    if os.path.exists(os.path.join(path, name)):
        raise FileExistsError("Filename '" + name + "' already exsits in '" + path + "'")


def strict(path, name):
    minimal(path, name)

    for char in name:
        if char not in VALID_CHARACTERS:
            raise NameError("Name '" + name + "' contains invalid character '" + char + "'.\n" +
                            "Valid characters are:\n" + VALID_CHARACTERS)


def thorough(path, name):
    minimal(path, name)

    for char in name:
        if char.lower() not in VALID_CHARACTERS:
            raise NameError("Name contains invalid character '" + char + "'.\n" +
                            "Valid characters are:\n" + VALID_CHARACTERS)

        for item in os.listdir(path):
            if name.lower() == item.lower():
                raise NameError("A directory with name (case independent) '" + name +
                                "' already exists and cannot be made according " +
                                "to the naming rule 'simple'.")


def none(path, name):
    pass
