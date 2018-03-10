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


def unique(parent_path, name):
    if name in parent_path.iterdir():
        raise FileExistsError(
            "'{}' already exists in '{}'".format(name, parent_path)
        )

def minimal(parent_path, name):
    unique(parent_path, name)
    name_str = str(name)

    if len(name_str) < 1:
        raise NameError("Name cannot be empty.")

    reserved_names = [
        exob.META_FILENAME,
        exob.ATTRIBUTES_FILENAME,
        exob.RAW_FOLDER_NAME
    ]

    dosnames = [
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3",
        "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6",
        "LPT7", "LPT8", "LPT9"
    ]

    if name_str in reserved_names:
        raise NameError(
            "Name cannot be '{}' because it is a reserved filename in Exdir.".format(name_str)
        )

    if name_str in dosnames:
        raise NameError(
            "Name cannot be '{}' because it is a reserved filename in Windows.".format(name_str)
        )


def strict(parent_path, name):
    unique(parent_path, name)
    minimal(parent_path, name)
    name_str = str(name)

    for char in name_str:
        if char not in VALID_CHARACTERS:
            raise NameError(
                "Name '{}' contains invalid character '{}'.\n"
                "Valid characters are:\n{}".format(name_str, char, VALID_CHARACTERS)
            )


def thorough(parent_path, name):
    minimal(parent_path, name)
    name_str = str(name)

    for char in name_str:
        if char.lower() not in VALID_CHARACTERS:
            raise NameError(
                "Name contains invalid character '{}'.\n"
                "Valid characters are:\n{}".format(char, VALID_CHARACTERS)
            )

    for item in parent_path.iterdir():
        if name_str != item.name and name_str.lower() == item.name.lower():
            raise FileExistsError(
                "A directory with name (case independent) '{}' already exists "
                " and cannot be made according to the naming rule 'thorough'.".format(name_str)
            )


def none(parent_path, name):
    pass
