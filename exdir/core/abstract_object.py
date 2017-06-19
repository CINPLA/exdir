from enum import Enum
import os
import yaml
import warnings
from . import filename_validation


class AbstractObject(object):
    """
    Parent class for exdir Group and exdir dataset objects
    """
    class OpenMode(Enum):
        READ_WRITE = 1
        READ_ONLY = 2

    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 naming_rule=None):
        self.root_directory = root_directory
        self.object_name = object_name
        self.parent_path = parent_path
        self.relative_path = os.path.join(self.parent_path, self.object_name)
        self.name = "/" + self.relative_path
        self.io_mode = io_mode

        naming_rule = naming_rule or filename_validation.simple

        if isinstance(naming_rule, str):
            if naming_rule == 'simple':
                naming_rule = filename_validation.simple
            elif naming_rule == 'strict':
                naming_rule = filename_validation.strict
            elif naming_rule == 'thorough':
                naming_rule = filename_validation.thorough
            elif naming_rule == 'none':
                naming_rule = filename_validation.none
            else:
                raise ValueError('IO name rule "' + naming_rule + '" not recognized,' +
                                 'name rule must be one of "strict", "simple", ' +
                                 '"thorough", "none"')

            warnings.warn(DeprecationWarning(
                "WARNING: naming_rule should be set to one of the functions in "
                "the filename_validation module. "
                "Defining naming rule by name is no longer supported."
            ))

        self.naming_rule = naming_rule

    @property
    def directory(self):
        return os.path.join(self.root_directory, self.relative_path)
