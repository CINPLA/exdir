from enum import Enum
import os
import yaml
import warnings
from . import filename_validation

# NOTE This is in a separate file only because of circular imports between Object and Raw otherwise
# TODO move this back to Object once circular imports are figured out

class AbstractObject(object):
    """
    Parent class for exdir Group and exdir dataset objects
    """
    class OpenMode(Enum):
        READ_WRITE = 1
        READ_ONLY = 2

    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 validate_name=None):
        self.root_directory = root_directory
        self.object_name = object_name
        self.parent_path = parent_path
        self.relative_path = os.path.join(self.parent_path, self.object_name)
        self.name = "/" + self.relative_path
        self.io_mode = io_mode

        validate_name = validate_name or filename_validation.thorough

        if isinstance(validate_name, str):
            if validate_name == 'simple':
                validate_name = filename_validation.thorough
            elif validate_name == 'strict':
                validate_name = filename_validation.strict
            elif validate_name == 'none':
                validate_name = filename_validation.none
            else:
                raise ValueError('IO name rule "' + validate_name + '" not recognized,' +
                                 'name rule must be one of "strict", "simple", ' +
                                 '"thorough", "none"')

            warnings.warn(
                "WARNING: validate_name should be set to one of the functions in " +
                "the filename_validation module. " +
                "Defining naming rule by string is no longer supported."
            )

        self.validate_name = validate_name

    @property
    def directory(self):
        return os.path.join(self.root_directory, self.relative_path)
