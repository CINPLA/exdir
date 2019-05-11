from __future__ import absolute_import, division, print_function, unicode_literals

from six import with_metaclass

from enum import Enum
import os
import warnings
import shutil
try:
    import pathlib
except ImportError as e:
    try:
        import pathlib2 as pathlib
    except ImportError:
        raise e
try:
    import ruamel_yaml as yaml
except ImportError:
    import ruamel.yaml as yaml

import exdir

from .. import utils
from .attribute import Attribute
from .constants import *
from .mode import assert_file_open, OpenMode

def _resolve_path(path):
    return pathlib.Path(path).resolve()


def _assert_valid_name(name, container):
    """Check if name (dataset or group) is valid."""
    container.file.name_validation(container.directory, name)


def _create_object_directory(directory, metadata):
    """
    Create object directory and meta file if directory
    don't already exist.
    """
    if directory.exists():
        raise IOError("The directory '" + str(directory) + "' already exists")
    valid_types = [DATASET_TYPENAME, FILE_TYPENAME, GROUP_TYPENAME]
    typename = metadata[EXDIR_METANAME][TYPE_METANAME]
    if typename not in valid_types:
        raise ValueError("{typename} is not a valid typename".format(typename=typename))
    directory.mkdir()
    meta_filename = directory / META_FILENAME
    with meta_filename.open("w", encoding="utf-8") as meta_file:
        if metadata == _default_metadata(typename):
            # if it is the default, we know how to print it fast
            metadata_string = (''
                '{exdir_meta}:\n'
                '   {type_meta}: "{typename}"\n'
                '   {version_meta}: {version}\n'
            '').format(
                exdir_meta=EXDIR_METANAME,
                type_meta=TYPE_METANAME,
                typename=typename,
                version_meta=VERSION_METANAME,
                version=1
            )
        else:
            metadata_string = yaml.dump(metadata)

        try:
            meta_file.write(metadata_string)
        except TypeError:
            # NOTE workaround for Python 2.7
            meta_file.write(metadata_string.decode('utf8'))


def _remove_object_directory(directory):
    """
    Remove object directory and meta file if directory exist.
    """
    if not directory.exists():
        raise IOError("The directory '" + str(directory) + "' does not exist")
    assert is_inside_exdir(directory)
    shutil.rmtree(directory)


def _default_metadata(typename):
    return {
        EXDIR_METANAME: {
            TYPE_METANAME: typename,
            VERSION_METANAME: 1
        }
    }


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
        raise RuntimeError("Path " + str(path) + " is not inside an Exdir repository.")


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

class Object(object):
    """
    Parent class for exdir Group and exdir dataset objects
    """
    def __init__(self, root_directory, parent_path, object_name, file):
        self.root_directory = root_directory
        self.object_name = str(object_name)  # NOTE could be path, so convert to str
        self.parent_path = parent_path
        self.relative_path = self.parent_path / self.object_name
        relative_name = str(self.relative_path)
        if relative_name == ".":
            relative_name = ""
        self.name = "/" + relative_name
        self.file = file

    @property # TODO consider warning if file is closed
    def directory(self):
        return self.root_directory / self.relative_path

    @property
    def attrs(self):
        assert_file_open(self.file)
        return Attribute(
            self,
            mode=Attribute._Mode.ATTRIBUTES,
            file=self.file,
        )

    @attrs.setter
    def attrs(self, value):
        assert_file_open(self.file)
        self.attrs._set_data(value)

    @property
    def meta(self):
        assert_file_open(self.file)
        return Attribute(
            self,
            mode=Attribute._Mode.METADATA,
            file=self.file,
        )

    @property # TODO consider warning if file is closed,
    def attributes_filename(self):
        return self.directory / ATTRIBUTES_FILENAME

    @property # TODO consider warning if file is closed
    def meta_filename(self):
        return self.directory / META_FILENAME

    def create_raw(self, name):
        from .raw import Raw
        assert_file_open(self.file)
        _assert_valid_name(name, self)
        directory_name = self.directory / name
        if directory_name.exists():
            raise FileExistsError("'{}' already exists in '{}'".format(name, self))
        directory_name.mkdir()
        return Raw(
            root_directory=self.root_directory,
            parent_path=self.relative_path,
            object_name=name,
            file=self.file
        )

    def require_raw(self, name):
        from .raw import Raw
        assert_file_open(self.file)
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
                file=self.file
            )

        return self.create_raw(name)

    @property
    def parent(self):
        from .group import Group
        assert_file_open(self.file)
        if len(self.parent_path.parts) < 1:
            return None
        parent_name = self.parent_path.name
        parent_parent_path = self.parent_path.parent
        return Group(
            root_directory=self.root_directory,
            parent_path=parent_parent_path,
            object_name=parent_name,
            file=self.file
        )

    def __eq__(self, other):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return False
        if not isinstance(other, Object):
            return False
        return (
            self.relative_path == other.relative_path and
            self.root_directory == other.root_directory
        )

    def __bool__(self):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return False
        return True

    def _repr_html_(self):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return None
        return exdir.utils.display.html_tree(self)

    def __repr__(self):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return "<Closed Exdir Group>"
        return "<Exdir Group '{}' (mode {})>".format(
            self.directory, self.file.user_mode)
