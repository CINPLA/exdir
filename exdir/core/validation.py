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

def _assert_unique(parent_path, name):
    if (parent_path / name).exists():
        raise FileExistsError(
            "'{}' already exists in '{}'".format(name, parent_path)
        )


def _assert_nonempty(parent_path, name):
    name_str = str(name)
    if len(name_str) < 1:
        raise NameError("Name cannot be empty.")


def _assert_nonreserved(name):
    name_str = str(name)

    reserved_names = [
        exob.META_FILENAME,
        exob.ATTRIBUTES_FILENAME,
        exob.RAW_FOLDER_NAME
    ]

    if name_str in reserved_names:
        raise NameError(
            "Name cannot be '{}' because it is a reserved filename in Exdir.".format(name_str)
        )

    if pathlib.PureWindowsPath(name).is_reserved():
        raise NameError(
            "Name cannot be '{}' because it is a reserved filename in Windows.".format(name_str)
        )


def unique(parent_path, name):
    _assert_nonempty(parent_path, name)
    _assert_unique(parent_path, name)


def minimal(parent_path, name):
    _assert_nonempty(parent_path, name)
    _assert_nonreserved(name)
    _assert_unique(parent_path, name)


def strict(parent_path, name):
    _assert_nonreserved(name)
    _assert_unique(parent_path, name)
    name_str = str(name)

    for char in name_str:
        if char not in VALID_CHARACTERS:
            raise NameError(
                "Name '{}' contains invalid character '{}'.\n"
                "Valid characters are:\n{}".format(name_str, char, VALID_CHARACTERS)
            )


def thorough(parent_path, name):
    _assert_nonempty(parent_path, name)
    _assert_nonreserved(name)
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
