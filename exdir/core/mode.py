from enum import Enum


class OpenMode(Enum):
    READ_WRITE = 1
    READ_ONLY = 2
    FILE_CLOSED = 3


def assert_file_open(func):
    """
    Decorator to check if the file is not closed.
    """
    def wrapper(self, *args, **kwargs):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            raise IOError("Unable to operate on closed File instance.")
        return func(self, *args, **kwargs)
    return wrapper


def assert_file_writable(func):
    """
    Decorator to check if the file is not closed,
    and that it is not in read only mode.
    """
    def wrapper(self, *args, **kwargs):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            raise IOError("Unable to operate on closed File instance.")
        if self.file.io_mode == OpenMode.READ_ONLY:
            raise IOError("Cannot change data on file in read only 'r' mode")
        return func(self, *args, **kwargs)
    return wrapper
