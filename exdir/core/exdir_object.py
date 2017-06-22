from enum import Enum
import os
import yaml
import warnings
import pathlib
from . import filename_validation

from . import exdir_object
from .. import utils
from .attribute import Attribute

# metadata
EXDIR_METANAME = "exdir"
TYPE_METANAME = "type"
VERSION_METANAME = "version"

# filenames
META_FILENAME = "exdir.yaml"
ATTRIBUTES_FILENAME = "attributes.yaml"
RAW_FOLDER_NAME = "__raw__"

# typenames
DATASET_TYPENAME = "dataset"
GROUP_TYPENAME = "group"
FILE_TYPENAME = "file"


def _assert_valid_name(name, container):
    """Check if name (dataset or group) is valid."""
    container.validate_name(container.directory, name)


def _create_object_directory(directory, typename):
    """
    Create object directory and meta file if directory
    don't already exist.
    """
    if directory.exists():
        raise IOError("The directory '" + str(directory) + "' already exists")
    valid_types = [DATASET_TYPENAME, FILE_TYPENAME, GROUP_TYPENAME]
    if typename not in valid_types:
        raise ValueError("{typename} is not a valid typename".format(typename=typename))
    directory.mkdir()
    meta_filename = directory / META_FILENAME
    with meta_filename.open("w", encoding="utf-8") as meta_file:
        metadata = {
            EXDIR_METANAME: {
                TYPE_METANAME: typename,
                VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)


def is_exdir_object(directory):
    """
    WARNING: Does not test if inside exdir directory,
    only if the object can be an exdir object (i.e. a directory).
    """
    return directory.is_dir()


def is_nonraw_object_directory(directory):
    meta_filename = directory / META_FILENAME
    if not meta_filename.exists():
        return False
    with meta_filename.open("r", encoding="utf-8") as meta_file:
        meta_data = yaml.safe_load(meta_file)

        if not isinstance(meta_data, dict):
            return False

        if EXDIR_METANAME not in meta_data:
            return False
        if TYPE_METANAME not in meta_data[EXDIR_METANAME]:
            return False
        valid_types = [DATASET_TYPENAME, FILE_TYPENAME, GROUP_TYPENAME]
        if meta_data[EXDIR_METANAME][TYPE_METANAME] not in valid_types:
            return False
    return True


def is_raw_object_directory(directory):
    return is_exdir_object(directory) and not is_nonraw_object_directory(directory)


def root_directory(path):
    """
    Iterates upwards until a exdir.File object is found.

    returns: path to exdir.File or None if not found.
    """
    path = pathlib.Path(path)
    found = False
    while not found:
        if path.parent == path:  # parent is self
            return None
        valid = is_nonraw_object_directory(path)
        if not valid:
            path = path.parent
            continue

        meta_filename = path / META_FILENAME
        with meta_filename.open("r", encoding="utf-8") as meta_file:
            meta_data = yaml.load(meta_file)
        if EXDIR_METANAME not in meta_data:
            path = path.parent
            continue
        exdir_meta = meta_data[EXDIR_METANAME]
        if TYPE_METANAME not in exdir_meta:
            path = path.parent
            continue
        if FILE_TYPENAME != exdir_meta[TYPE_METANAME]:
            path = path.parent
            continue
        found = True
    return path


def is_inside_exdir(path):
    path = pathlib.Path(path)
    return root_directory(path) is not None


def assert_inside_exdir(path):
    path = pathlib.Path(path)
    if not is_inside_exdir(path):
        raise FileNotFoundError("Path " + str(path) + " is not inside an Exdir repository.")


def open_object(path):
    from . import exdir_file
    path = pathlib.Path(path)
    assert_inside_exdir(path)
    root_dir = root_directory(path)
    object_name = path.relative_to(root_dir)
    object_name = object_name.as_posix()
    exdir_file = exdir_file.File(root_dir)
    if object_name == ".":
        return exdir_file
    return exdir_file[object_name]

# NOTE This is in a separate file only because of circular imports between Object and Raw otherwise
# TODO move this back to Object once circular imports are figured out


class Object():
    """
    Parent class for exdir Group and exdir dataset objects
    """
    class OpenMode(Enum):
        READ_WRITE = 1
        READ_ONLY = 2

    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 validate_name=None):
        self.root_directory = root_directory
        self.object_name = str(object_name)  # NOTE could be path, so convert to str
        self.parent_path = parent_path
        self.relative_path = self.parent_path / self.object_name
        self.name = "/" + str(self.relative_path)
        self.io_mode = io_mode

        validate_name = validate_name or filename_validation.thorough

        if isinstance(validate_name, str):
            if validate_name == 'simple':
                validate_name = filename_validation.thorough
            elif validate_name == 'thorough':
                validate_name = filename_validation.thorough
            elif validate_name == 'strict':
                validate_name = filename_validation.strict
            elif validate_name == 'none':
                validate_name = filename_validation.none
            else:
                raise ValueError(
                    'IO name rule "' + validate_name + '" not recognized,' +
                    'name rule must be one of "strict", "simple", ' +
                    '"thorough", "none"'
                )

            warnings.warn(
                "WARNING: validate_name should be set to one of the functions in " +
                "the exdir.filename_validation module. " +
                "Defining naming rule by string is no longer supported."
            )

        self.validate_name = validate_name

    @property
    def directory(self):
        return self.root_directory / self.relative_path

    @property
    def attrs(self):
        return Attribute(self, mode=Attribute.Mode.ATTRIBUTES,
                         io_mode=self.io_mode)

    @attrs.setter
    def attrs(self, value):
        self.attrs._set_data(value)

    @property
    def meta(self):
        return Attribute(self, mode=Attribute.Mode.METADATA,
                         io_mode=self.io_mode)

    @property
    def attributes_filename(self):
        return self.directory / ATTRIBUTES_FILENAME

    @property
    def meta_filename(self):
        return self.directory / META_FILENAME

    def create_raw(self, name):
        from .raw import Raw
        _assert_valid_name(name, self)
        directory_name = self.directory / name
        if directory_name.exists():
            raise FileExistsError("'{}' already exists in '{}'".format(name, self))
        directory_name.mkdir()
        return Raw(
            self.root_directory,
            self.parent_path,
            name,
            io_mode=self.io_mode
        )

    def require_raw(self, name):
        directory_name = self.directory / name
        if directory_name.exists():
            if is_nonraw_object_directory(directory_name):
                raise FileExistsError("Directory '" + directory_name + "' already exists, but is not raw.")
            return directory_name

        return self.create_raw(name)

    @property
    def parent(self):
        from .group import Group
        if len(self.parent_path.parts) < 1:
            return None
        parent_name = self.parent_path.name
        parent_parent_path = self.parent_path.parent
        return Group(
            root_directory=self.root_directory,
            parent_path=parent_parent_path,
            object_name=parent_name,
            io_mode=self.io_mode,
            validate_name=self.validate_name
        )

    def __eq__(self, other):
        if not isinstance(other, Object):
            return False
        return (
            self.relative_path == other.relative_path and
            self.root_directory == other.root_directory
        )
