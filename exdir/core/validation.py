from enum import Enum
import os
try:
    import pathlib
except ImportError as e:
    try:
        import pathlib2 as pathlib
    except ImportError:
        raise e
from . import constants as exob

VALID_CHARACTERS = ("abcdefghijklmnopqrstuvwxyz1234567890_-.")


class NamingRule(Enum):
    SIMPLE = 1
    STRICT = 2
    THOROUGH = 3
    NONE = 4

def _assert_unique(parent_path, name):
    try:
        name_str = str(name)
    except UnicodeEncodeError:
        name = name.encode('utf8')

    if (parent_path / name).exists():
        raise RuntimeError(
            "'{}' already exists in '{}'".format(name, parent_path)
        )


def _assert_nonempty(parent_path, name):
    try:
        name_str = str(name)
    except UnicodeEncodeError:
        name_str = name.encode('utf8')

    if len(name_str) < 1:
        raise NameError("Name cannot be empty.")


def _assert_nonreserved(name):
    # NOTE ignore unicode errors, they are not reserved
    try:
        name_str = str(name)
    except UnicodeEncodeError:
        name_str = name.encode('utf8')

    reserved_names = [
        exob.META_FILENAME,
        exob.ATTRIBUTES_FILENAME,
        exob.RAW_FOLDER_NAME
    ]

    if name_str in reserved_names:
        raise NameError(
            "Name cannot be '{}' because it is a reserved filename in Exdir.".format(name_str)
        )

    if pathlib.PureWindowsPath(name_str).is_reserved():
        raise NameError(
            "Name cannot be '{}' because it is a reserved filename in Windows.".format(name_str)
        )

def _assert_valid_characters(name):
    try:
        name_str = str(name)
    except UnicodeEncodeError:
        name_str = name.encode('utf8')

    for char in name_str:
        if char not in VALID_CHARACTERS:
            raise NameError(
                "Name '{}' contains invalid character '{}'.\n"
                "Valid characters are:\n{}".format(name_str, char, VALID_CHARACTERS)
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
    _assert_valid_characters(name)

def thorough(parent_path, name):
    _assert_nonempty(parent_path, name)
    _assert_nonreserved(name)
    try:
        name_str = str(name)
    except UnicodeEncodeError:
        name_str = name.encode('utf8')
    name_lower = name_str.lower()
    _assert_valid_characters(name_lower)

    if isinstance(pathlib.Path(parent_path), pathlib.WindowsPath):
        # use _assert_unique if we're already on Windows, because it is much faster
        # than the test below
        _assert_unique(parent_path, name)
        return

    # os.listdir is much faster here than os.walk or parent_path.iterdir
    for item in os.listdir(str(parent_path)):
        if name_lower == item.lower():
            raise RuntimeError(
                "A directory with name (case independent) '{}' already exists "
                " and cannot be made according to the naming rule 'thorough'.".format(name)
            )


def none(parent_path, name):
    pass
