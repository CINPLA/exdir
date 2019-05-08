from enum import Enum


class OpenMode(Enum):
    READ_WRITE = 1
    READ_ONLY = 2
    FILE_CLOSED = 3


def assert_file_open(func):
    def wrapper(self, *args, **kwargs):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            raise IOError("Unable to operate on closed File instance.")
        return func(self, *args, **kwargs)
    return wrapper
