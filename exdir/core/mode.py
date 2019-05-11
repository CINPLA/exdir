from enum import Enum


class OpenMode(Enum):
    READ_WRITE = 1
    READ_ONLY = 2
    FILE_CLOSED = 3


def assert_file_open(file_object):
    """
    Decorator to check if the file is not closed.
    """
    if file_object.io_mode == OpenMode.FILE_CLOSED:
        raise IOError("Unable to operate on closed File instance.")


def assert_file_writable(file_object):
    """
    Decorator to check if the file is not closed,
    and that it is not in read only mode.
    """
    if file_object.io_mode == OpenMode.FILE_CLOSED:
        raise IOError("Unable to operate on closed File instance.")
    if file_object.io_mode == OpenMode.READ_ONLY:
        raise IOError("Cannot change data on file in read only 'r' mode")
