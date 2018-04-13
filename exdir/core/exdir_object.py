from enum import Enum
import os
import ruamel_yaml as yaml
import warnings
import pathlib
from . import validation

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

def _resolve_path(path):
    return pathlib.Path(path).resolve()


def _assert_valid_name(name, container):
    """Check if name (dataset or group) is valid."""
    container.name_validation(container.directory, name)


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
        metadata = """
{exdir_meta}:
    {type_meta}: "{typename}"
    {version_meta}: {version}
""".format(
        exdir_meta=EXDIR_METANAME,
        type_meta=TYPE_METANAME,
        typename=typename,
        version_meta=VERSION_METANAME,
        version=1
    )
        meta_file.write(metadata)


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
    path = _resolve_path(path)
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
            meta_data = yaml.safe_load(meta_file)
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
    path = _resolve_path(path)
    return root_directory(path) is not None


def assert_inside_exdir(path):
    path = _resolve_path(path)
    if not is_inside_exdir(path):
        raise FileNotFoundError("Path " + str(path) + " is not inside an Exdir repository.")


def open_object(path):
    from . import exdir_file
    path = _resolve_path(path)
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

# Meta class to make subclasses pick up on Groups documentation
class ObjectMeta(type):
    def __new__(mcls, classname, bases, cls_dict):
        cls = super().__new__(mcls, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if not getattr(member, '__doc__') and hasattr(bases[-1], name) and getattr(getattr(bases[-1], name), "__doc__"):
                member.__doc__ = getattr(bases[-1], name).__doc__
        return cls

class Object(object, metaclass=ObjectMeta):
    """
    Parent class for exdir Group and exdir dataset objects
    """
    class OpenMode(Enum):
        READ_WRITE = 1
        READ_ONLY = 2

    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 name_validation=None, plugin_manager=None):
        # TODO put io_mode, name_validation, plugin_types into a configuration object
        self.root_directory = root_directory
        self.object_name = str(object_name)  # NOTE could be path, so convert to str
        self.parent_path = parent_path
        self.relative_path = self.parent_path / self.object_name
        relative_name = str(self.relative_path)
        if relative_name == ".":
            relative_name = ""
        self.name = "/" + relative_name
        self.io_mode = io_mode
        self.plugin_manager = plugin_manager

        name_validation = name_validation or validation.thorough

        if isinstance(name_validation, str):
            if name_validation == 'simple':
                name_validation = validation.thorough
            elif name_validation == 'thorough':
                name_validation = validation.thorough
            elif name_validation == 'strict':
                name_validation = validation.strict
            elif name_validation == 'none':
                name_validation = validation.none
            else:
                raise ValueError(
                    'IO name rule "{}" not recognized, '
                    'name rule must be one of "strict", "simple", '
                    '"thorough", "none"'.format(name_validation)
                )

            warnings.warn(
                "WARNING: name_validation should be set to one of the functions in "
                "the exdir.validation module. "
                "Defining naming rule by string is no longer supported."
            )

        self.name_validation = name_validation

    @property
    def directory(self):
        return self.root_directory / self.relative_path

    @property
    def attrs(self):
        return Attribute(
            self,
            mode=Attribute.Mode.ATTRIBUTES,
            io_mode=self.io_mode,
            plugin_manager=self.plugin_manager
        )

    @attrs.setter
    def attrs(self, value):
        self.attrs._set_data(value)

    @property
    def meta(self):
        return Attribute(
            self,
            mode=Attribute.Mode.METADATA,
            io_mode=self.io_mode,
            plugin_manager=self.plugin_manager
        )

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
            root_directory=self.root_directory,
            parent_path=self.relative_path,
            object_name=name,
            io_mode=self.io_mode
        )

    def require_raw(self, name):
        from .raw import Raw
        directory_name = self.directory / name
        if directory_name.exists():
            if is_nonraw_object_directory(directory_name):
                raise FileExistsError(
                    "Directory '{}' already exists, but is not raw.".format(directory_name)
                )
            return Raw(
                root_directory=self.root_directory,
                parent_path=self.relative_path,
                object_name=name,
                io_mode=self.io_mode
            )

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
            name_validation=self.name_validation,
            plugin_manager=self.plugin_manager
        )

    def __eq__(self, other):
        if not isinstance(other, Object):
            return False
        return (
            self.relative_path == other.relative_path and
            self.root_directory == other.root_directory
        )
