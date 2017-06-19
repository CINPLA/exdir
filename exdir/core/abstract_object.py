from enum import Enum
import os
import yaml


class AbstractObject(object):
    """
    Parent class for exdir Group and exdir dataset objects
    """
    class OpenMode(Enum):
        READ_WRITE = 1
        READ_ONLY = 2

    class NamingRule(Enum):
        SIMPLE = 1
        STRICT = 2
        THOROUGH = 3
        NONE = 4

    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 naming_rule=None):
        self.root_directory = root_directory
        self.object_name = object_name
        self.parent_path = parent_path
        self.relative_path = os.path.join(self.parent_path, self.object_name)
        self.name = "/" + self.relative_path
        self.io_mode = io_mode
        self.naming_rule = naming_rule

    @property
    def directory(self):
        return os.path.join(self.root_directory, self.relative_path)
