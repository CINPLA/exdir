# -*- coding: utf-8 -*-

"""
.. module:: exdir.core
.. moduleauthor:: Svenn-Arne Dragly, Milad H. Mobarhan, Mikkel E. Lepperød
"""

from __future__ import print_function, division, unicode_literals

import os
import yaml
import numpy as np
import shutil
import quantities as pq
from collections.abc import KeysView, ValuesView, ItemsView
import re
from enum import Enum

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


def natural_sort(l):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(l, key=alphanum_key)


def convert_back_quantities(value):
    """Convert quantities back from dictionary."""
    result = value
    if isinstance(value, dict):
        if "unit" in value and "value" in value and "uncertainty" in value:
            try:
                result = pq.UncertainQuantity(value["value"],
                                              value["unit"],
                                              value["uncertainty"])
            except Exception:
                pass
        elif "unit" in value and "value" in value:
            try:
                result = pq.Quantity(value["value"], value["unit"])
            except Exception:
                pass
        else:
            try:
                for key, value in result.items():
                    result[key] = convert_back_quantities(value)
            except AttributeError:
                pass

    return result


def convert_quantities(value):
    """Convert quantities to dictionary."""

    result = value
    if isinstance(value, pq.Quantity):
        result = {
            "value": value.magnitude.tolist(),
            "unit": value.dimensionality.string
        }
        if isinstance(value, pq.UncertainQuantity):
            assert value.dimensionality == value.uncertainty.dimensionality
            result["uncertainty"] = value.uncertainty.magnitude.tolist()
    elif isinstance(value, np.ndarray):
        result = value.tolist()
    elif isinstance(value, np.integer):
        result = int(value)
    elif isinstance(value, np.float):
        result = float(value)
    else:
        # try if dictionary like objects can be converted if not return the
        # original object
        # Note, this might fail if .items() returns a strange combination of
        # objects
        try:
            new_result = {}
            for key, val in value.items():
                new_key = convert_quantities(key)
                new_result[new_key] = convert_quantities(val)
            result = new_result
        except AttributeError:
            pass

    return result


def _assert_valid_name(name, container):
    """Check if name (dataset or group) is valid."""
    valid_characters = ("abcdefghijklmnopqrstuvwxyz1234567890_-")

    if len(name) < 1:
        raise NameError("Name cannot be empty.")

    if container.naming_rule == Object.NamingRule.THOROUGH:
        raise NotImplementedError

    if container.naming_rule == Object.NamingRule.STRICT:
        for char in name:
            if char not in valid_characters:
                raise NameError("Name contains invalid character '" + char + "'.\n"
                                + "Valid characters are:\n" + valid_characters)

    if container.naming_rule == Object.NamingRule.SIMPLE:
        for char in name:
            if char.lower() not in valid_characters:
                raise NameError("Name contains invalid character '" + char + "'.\n"
                                + "Valid characters are:\n" + valid_characters)

            if name.lower() in [nm.lower() for nm in container]:
                raise NameError("An object with name (case independent) '" + name +
                                "' already exists and cannot be made according " +
                                "to the naming rule 'simple'.")


    dosnames = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3",
                "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6",
                "LPT7", "LPT8", "LPT9"]


    invalid_names = [META_FILENAME,
                     ATTRIBUTES_FILENAME,
                     RAW_FOLDER_NAME]

    if name in invalid_names:
        raise NameError("Name cannot be '" + name + "'.")



def _create_object_directory(directory, typename):
    """
    Create object directory and meta file if directory
    don't already exist.
    """
    if os.path.exists(directory):
        raise IOError("The directory '" + directory + "' already exists")
    valid_types = [DATASET_TYPENAME, FILE_TYPENAME, GROUP_TYPENAME]
    if typename not in valid_types:
        raise ValueError("{typename} is not a valid typename".format(typename=typename))
    os.mkdir(directory)
    meta_filename = _metafile_from_directory(directory)
    with open(meta_filename, "w") as meta_file:
        metadata = {
            EXDIR_METANAME: {
                TYPE_METANAME: typename,
                VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)


def _metafile_from_directory(directory):
    return os.path.join(directory, META_FILENAME)


def _is_exdir_object(directory):
    """
    WARNING: Does not test if inside exdir directory,
    only if the object can be an exdir object (i.e. a directory).
    """
    return os.path.isdir(directory)


def _is_nonraw_object_directory(directory):
    meta_filename = os.path.join(directory, META_FILENAME)
    if not os.path.exists(meta_filename):
        return False
    with open(meta_filename, "r") as meta_file:
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


def _is_raw_object_directory(directory):
    return _is_exdir_object(directory) and not _is_nonraw_object_directory(directory)


def root_directory(path):
    """
    Iterates upwards until a exdir.File object is found.

    returns: path to exdir.File or None if not found.
    """
    path = os.path.abspath(path)
    found = False
    while not found:
        if os.path.dirname(path) == path:  # parent is self
            return None
        valid = _is_nonraw_object_directory(path)
        if not valid:
            path = os.path.dirname(os.path.abspath(path))
            continue

        meta_filename = _metafile_from_directory(path)
        with open(meta_filename, "r") as meta_file:
            meta_data = yaml.load(meta_file)
        if EXDIR_METANAME not in meta_data:
            path = os.path.dirname(os.path.abspath(path))
            continue
        exdir_meta = meta_data[EXDIR_METANAME]
        if TYPE_METANAME not in exdir_meta:
            path = os.path.dirname(os.path.abspath(path))
            continue
        if FILE_TYPENAME != exdir_meta[TYPE_METANAME]:
            path = os.path.dirname(os.path.abspath(path))
            continue
        found = True
    return path


def is_inside_exdir(path):
    path = os.path.abspath(path)
    return root_directory(path) is not None


def assert_inside_exdir(path):
    path = os.path.abspath(path)
    if not is_inside_exdir(path):
        raise FileNotFoundError("Path " + path + " is not inside an Exdir repository.")


def open_object(path):
    path = os.path.abspath(path)
    assert_inside_exdir(path)
    root_dir = root_directory(path)
    object_name = os.path.relpath(path, root_dir)
    object_name = object_name.replace(os.sep, "/")
    exdir_file = File(root_dir)
    if object_name == ".":
        return exdir_file
    return exdir_file[object_name]


class Attribute(object):
    """Attribute class."""

    class Mode(Enum):
        ATTRIBUTES = 1
        METADATA = 2

    def __init__(self, parent, mode, io_mode, path=None):
        self.parent = parent
        self.mode = mode
        self.io_mode = io_mode
        self.path = path or []

    def __getitem__(self, name=None):
        meta_data = self._open_or_create()
        convert_back_quantities(meta_data)
        for i in self.path:
            meta_data = meta_data[i]
        if name is not None:
            meta_data = meta_data[name]
        if isinstance(meta_data, dict):
            return Attribute(self.parent, self.mode, self.io_mode,
                             self.path + [name])
        else:
            return meta_data

    def __setitem__(self, name, value):
        meta_data = self._open_or_create()

        # if isinstance(name, np.integer):
        #     key = int(name)
        # else:
        #     key = name
        key = name

        sub_meta_data = meta_data
        for i in self.path:
            sub_meta_data = sub_meta_data[i]
        sub_meta_data[key] = value

        self._set_data(meta_data)

    def __contains__(self, name):
        meta_data = self._open_or_create()
        for i in self.path:
            meta_data = meta_data[i]
        return name in meta_data

    def keys(self):
        meta_data = self._open_or_create()
        for i in self.path:
            meta_data = meta_data[i]
        return meta_data.keys()

    def to_dict(self):
        meta_data = self._open_or_create()
        for i in self.path: # TODO check if this is necesary
            meta_data = meta_data[i]
        meta_data = convert_back_quantities(meta_data)
        return meta_data

    def items(self):
        meta_data = self._open_or_create()
        for i in self.path:
            meta_data = meta_data[i]
        return meta_data.items()

    def values(self):
        meta_data = self._open_or_create()
        for i in self.path:
            meta_data = meta_data[i]
        return meta_data.values()

    def _set_data(self, meta_data):
        if self.io_mode == Object.OpenMode.READ_ONLY:
            raise IOError("Cannot write in read only ("r") mode")
        meta_data = convert_quantities(meta_data)
        with open(self.filename, "w") as meta_file:
            yaml.safe_dump(meta_data,
                           meta_file,
                           default_flow_style=False,
                           allow_unicode=True)

    # TODO only needs filename, make into free function
    def _open_or_create(self):
        meta_data = {}
        if os.path.exists(self.filename):
            with open(self.filename, "r") as meta_file:
                meta_data = yaml.safe_load(meta_file)
        return meta_data

    def __iter__(self):
        for key in self.keys():
            yield key

    @property
    def filename(self):
        if self.mode == self.Mode.METADATA:
            return self.parent.meta_filename
        else:
            return self.parent.attributes_filename

    def __len__(self):
        return len(self.keys())

class Object(object):
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
    def directory(self):
        return os.path.join(self.root_directory, self.relative_path)

    @property
    def attributes_filename(self):
        return os.path.join(self.directory, ATTRIBUTES_FILENAME)

    @property
    def meta_filename(self):
        return _metafile_from_directory(self.directory)

    def create_raw(self, name):
        directory_name = os.path.join(self.directory, name)
        if os.path.exists(directory_name):
            raise IOError("Raw directory " + directory_name +
                          " already exists.")
        os.mkdir(directory_name)
        return directory_name

    def require_raw(self, name):
        directory_name = os.path.join(self.directory, name)
        if os.path.exists(directory_name):
            return directory_name
        else:
            return self.create_raw(name)


class Raw(Object):
    """
    Raw objects are simple folders with any content.

    Raw objects currently have no features apart from showing their path.
    """
    def __init__(self, root_directory, parent_path, object_name, io_mode=None):
        super(Raw, self).__init__(root_directory=root_directory,
                                  parent_path=parent_path,
                                  object_name=object_name, io_mode=io_mode)


class Group(Object):
    """
    Container of other groups and datasets.
    """


    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 naming_rule=None):
        super(Group, self).__init__(root_directory=root_directory,
                                    parent_path=parent_path,
                                    object_name=object_name, io_mode=io_mode,
                                    naming_rule=naming_rule)

    def create_dataset(self, name, shape=None, dtype=None, data=None, fillvalue=None):
        _assert_valid_name(name, self)
        dataset_directory = os.path.join(self.directory, name)
        _create_object_directory(dataset_directory, DATASET_TYPENAME)
        # TODO check dimensions, npy or npz
        dataset = Dataset(root_directory=self.root_directory,
                          parent_path=self.relative_path, object_name=name,
                          io_mode=self.io_mode,
                          naming_rule=self.naming_rule)

        dataset.set_data(shape=shape, dtype=dtype, data=data, fillvalue=fillvalue)

        return dataset

    def create_group(self, name):
        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError("Cannot write data to file in read only ("r") mode")

        if name.startswith("/"):
            raise NotImplementedError("Creating a group in the absolute directory " +
                                      "from a subgroup is currently not supported " +
                                      "and is unlikely to be implemented.")

        if name.endswith("/"):
            name = name.rstrip("/")

        if "/" in name:
            raise NotImplementedError("Intermediate groups can not yet be " +
                                      "created automatically.")

        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError("Cannot write data to file in read only ("r") mode")


        _assert_valid_name(name, self)
        group_directory = os.path.join(self.directory, name)
        _create_object_directory(group_directory, GROUP_TYPENAME)
        group = Group(root_directory=self.root_directory,
                      parent_path=self.relative_path, object_name=name,
                      io_mode=self.io_mode,
                      naming_rule=self.naming_rule)
        return group

    def require_group(self, name):
        if name.startswith("/"):
            raise NotImplementedError("Requiring a group in the absolute directory " +
                                      "from a subgroup is currently not supported " +
                                      "and is unlikely to be implemented.")

        if name.endswith("/"):
            name = name.rstrip("/")

        group_directory = os.path.join(self.directory, name)
        if name in self:
            current_object = self[name]
            if isinstance(current_object, Group):
                return current_object
            else:
                raise TypeError("An object with name '" + name + "' already " +
                                "exists, but it is not a Group.")
        elif os.path.exists(group_directory):
            raise IOError("Directory " + group_directory + " already exists," +
                          " but is not an Exdir object.")
        else:
            return self.create_group(name)

    @property
    def parent(self):
        parent = self.parent_path.split(os.sep)[-1]
        parent_parent = os.sep.join(self.parent_path.split(os.sep)[:-1])
        return Group(root_directory=self.root_directory,
                     parent_path=parent_parent, object_name=parent,
                     io_mode=self.io_mode,
                     naming_rule=self.naming_rule)

    def require_dataset(self, name, shape=None, dtype=None, data=None, fillvalue=None):
        if name in self:
            current_object = self[name]

            if not isinstance(current_object, Dataset):
                msg = "Incompatible object ({}) already exists".format(current_object.__class__.__name__)
                raise TypeError(msg)


            if shape is not None:
                if not np.array_equal(shape, current_object.shape):
                    msg = "Shapes do not match (existing {} vs new {})".format(current_object.shape, shape)
                    raise TypeError(msg)

            if dtype is not None:
                if dtype != current_object.dtype:
                    msg = "Datatypes do not exactly match (existing {} vs new {})".format(current_object.dtype, dtype)
                    raise TypeError(msg)

                # if not numpy.can_cast(dtype, dset.dtype):
                #     msg = "Datatypes cannot be safely cast (existing {} vs new {})".format(dset.dtype, dtype)
                #     raise TypeError(msg)

            # TODO is this correct or should we throw a typeerror if data is not similar to data?
            #      This can potentially overwrite data
            if data is None:
                return current_object
            else:
                current_object.set_data(data)
                return current_object

        else:
            return self.create_dataset(name, shape=shape, dtype=dtype,
                                       data=data, fillvalue=fillvalue)


    def __contains__(self, name):
        if len(name) < 1:
            return False

        if name.startswith("/"):
            raise NotImplementedError("Testing if name in a group in the root directory " +
                                      "from a subgroup is currently not supported " +
                                      "and is unlikely to be implemented.")

        if name.endswith("/"):
            name = name.rstrip("/")

        directory = os.path.join(self.directory, name)

        return _is_exdir_object(directory)

    def __getitem__(self, name):
        if name.endswith("/"):
            name = name.rstrip("/")

        if name.startswith("/"):
            raise NotImplementedError("Getting a group in the root directory " +
                                      "from a subgroup is currently not supported " +
                                      "and is unlikely to be implemented.")

        if "/" in name:
            name_split = name.split("/", 1)
            if len(name_split) == 2:
                item = self[name_split[0]]
                return item[name_split[1]]
            else:
                return self[name_split[0]]

        directory = os.path.join(self.directory, name)
        if name not in self:
            raise KeyError("No such object: '" + name + "'")

        if _is_raw_object_directory(directory):
            return Raw(root_directory=self.root_directory,
                       parent_path=self.relative_path,
                       object_name=name,
                       io_mode=self.io_mode)

        if not _is_nonraw_object_directory(directory):
            raise IOError("Directory '" + directory +
                          "' is not a valid exdir object.")

        meta_filename = os.path.join(self.directory, name, META_FILENAME)
        with open(meta_filename, "r") as meta_file:
            meta_data = yaml.safe_load(meta_file)
        if meta_data[EXDIR_METANAME][TYPE_METANAME] == DATASET_TYPENAME:
            return Dataset(root_directory=self.root_directory,
                           parent_path=self.relative_path,
                           object_name=name,
                           io_mode=self.io_mode,
                           naming_rule=self.naming_rule)
        elif meta_data[EXDIR_METANAME][TYPE_METANAME] == GROUP_TYPENAME:
            return Group(root_directory=self.root_directory,
                         parent_path=self.relative_path,
                         object_name=name,
                         io_mode=self.io_mode,
                         naming_rule=self.naming_rule)
        else:
            print("Object", name, "has data type", meta_data[EXDIR_METANAME][TYPE_METANAME])
            raise NotImplementedError("Cannot open objects of this type")


    def __setitem__(self, name, value):
        if name not in self:
            self.create_dataset(name, data=value)
        else:
            current_item = self.__getitem__(name)
            if isinstance(current_item, Dataset):
                print("Is dataset")
            else:
                print("Data type")
                raise NotImplementedError("Only dataset writing implemented")

    def keys(self):
        return KeysView(self)

    def items(self):
        return ItemsView(self)

    def values(self):
        return ValuesView(self)

    def __iter__(self):
        for name in natural_sort(os.listdir(self.directory)):
            if name in self:
                yield name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False



class File(Group):
    """Exdir file object."""

    def __init__(self, directory, mode=None, allow_remove=False,
                 naming_rule=None):
        if not directory.endswith(".exdir"):
            directory = directory + ".exdir"
        mode = mode or 'a'
        recognized_modes = ['a', 'r', 'r+', 'w', 'w-', 'x', 'a']
        if mode not in recognized_modes:
            raise ValueError('IO mode "' + mode + '" not recognized,' +
                             'mode must be one of {}'.format(recognized_modes))
        if mode == "r":
            self.io_mode = self.OpenMode.READ_ONLY
        else:
            self.io_mode = self.OpenMode.READ_WRITE

        naming_rule = naming_rule or 'simple'
        if naming_rule == 'simple':
            self.naming_rule = self.NamingRule.SIMPLE
        elif naming_rule == 'strict':
            self.naming_rule = self.NamingRule.STRICT
        elif naming_rule == 'thorough':
            self.naming_rule = self.NamingRule.THOROUGH
        elif naming_rule == 'none':
            self.naming_rule = self.NamingRule.NONE
        else:
            raise ValueError('IO name rule "' + naming_rule + '" not recognized,' +
                             'name rule must be one of "strict", "simple", ' +
                             '"thorough", "none"')

        super(File, self).__init__(root_directory=directory,
                                   parent_path="", object_name="",
                                   io_mode=self.io_mode,
                                   naming_rule=self.naming_rule)

        already_exists = os.path.exists(directory)
        if already_exists:
            if not _is_nonraw_object_directory(directory):
                raise FileExistsError("Path '" + directory +
                                      "' already exists, but is not a valid " +
                                      "exdir file.")
            if self.meta[EXDIR_METANAME][TYPE_METANAME] != FILE_TYPENAME:
                raise FileExistsError("Path '" + directory +
                                      "' already exists, but is not a valid " +
                                      "exdir file.")




        should_create_directory = False

        if mode == "r":
            if not already_exists:
                raise IOError("File " + directory + " does not exist.")
        elif mode == "r+":
            if not already_exists:
                raise IOError("File " + directory + " does not exist.")
        elif mode == "w":
            if already_exists:
                if allow_remove:
                    shutil.rmtree(directory)
                else:
                    raise FileExistsError(
                        "File " + directory + " already exists. We won't delete the entire tree" +
                        " by default. Add allow_remove=True to override."
                    )
            should_create_directory = True
        elif mode == "w-" or mode == "x":
            if already_exists:
                raise IOError("File " + directory + " already exists.")
            should_create_directory = True
        elif mode == "a":
            if not already_exists:
                should_create_directory = True


        valid_characters = ("abcdefghijklmnopqrstuvwxyz1234567890_-.")
        if should_create_directory:
            path, name = os.path.split(directory)
            if path == "":
                path = "."

            if self.naming_rule == Object.NamingRule.THOROUGH:
                raise NotImplementedError

            elif self.naming_rule == Object.NamingRule.STRICT:
                for char in name:
                    if char not in valid_characters:
                        raise NameError("Name contains invalid character '" + char + "'.\n"
                                        + "Valid characters are:\n" + valid_characters)

            elif self.naming_rule == Object.NamingRule.SIMPLE:
                for char in name:
                    if char.lower() not in valid_characters:
                        raise FileExistsError("Name contains invalid character '" + char + "'.\n"
                                              + "Valid characters are:\n" + valid_characters)

                    for item in os.listdir(path):
                        if name.lower() == item.lower():
                            raise NameError("A directory with name (case independent) '" + name +
                                            "' already exists and cannot be made according " +
                                            "to the naming rule 'simple'.")

            invalid_names = [META_FILENAME,
                             ATTRIBUTES_FILENAME,
                             RAW_FOLDER_NAME]

            if name in invalid_names:
                raise NameError("Name cannot be '" + name + "'.")


            _create_object_directory(directory, FILE_TYPENAME)

    def close(self):
        # yeah right, as if we would create a real file format
        pass


    def create_group(self, name):
        if name.startswith("/"):
            name = name[1:]

        return super().create_group(name)

    def require_group(self, name):
        if name.startswith("/"):
            name = name[1:]

        return super().require_group(name)

    def __getitem__(self, name):
        if name.startswith("/"):
            if name == "/":
                return self
            else:
                name = name[1:]

        return super().__getitem__(name)


    def __contains__(self, name):
        if name.startswith("/"):
            if name == "/":
                return True
            name = name[1:]

        return super().__contains__(name)


class Dataset(Object):
    """
    Dataset class

    Warning: MODIFIES VIEW!!!!!!! different from h5py
    Warning: Possible to overwrite existing dataset.
             This differs from the h5py API. However,
             it should only cause issues with existing
             code if said code expects this to fail."
    """
    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 naming_rule=None):
        super(Dataset, self).__init__(root_directory=root_directory,
                                      parent_path=parent_path,
                                      object_name=object_name,
                                      io_mode=io_mode,
                                      naming_rule=naming_rule)
        self.data_filename = os.path.join(self.directory, "data.npy")
        self._data = None
        if self.io_mode == self.OpenMode.READ_ONLY:
            self._mmap_mode = "r"
        else:
            self._mmap_mode = "r+"

    # TODO make support for creating a quantities array
    def set_data(self, shape=None, dtype=None, data=None, fillvalue=None):
        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError("Cannot write data to file in read only ('r') mode")


        if data is not None:
            if isinstance(data, pq.Quantity):
                result = data.magnitude
                self.attrs["unit"] = data.dimensionality.string
                if isinstance(data, pq.UncertainQuantity):
                    self.attrs["uncertainty"] = data.uncertainty
            else:
                result = data

            if not isinstance(result, np.ndarray):
                result = np.asarray(data, order="C", dtype=dtype)

            if shape is not None and result.shape != shape:
                result = np.reshape(result, shape)
        else:
            if shape is None:
                result = None
            else:
                fillvalue = fillvalue or 0.0
                result = np.full(shape, fillvalue, dtype=dtype)

        if result is not None:
            np.save(self.data_filename, result)

            # TODO should we have this line?
            #      Might lead to bugs where we create data, but havent loaded it
            #      but requires the data always stay in memory
            # self._data = result


    def __getitem__(self, args):
        if not os.path.exists(self.data_filename):
            return np.array([])
        if self._data is None:
            self._data = np.load(self.data_filename, mmap_mode=self._mmap_mode)
        if len(self._data.shape) == 0:
            return self._data
        else:
            return self._data[args]

    def __setitem__(self, args, value):
        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError('Cannot write data to file in read only ("r") mode')
        if self._data is None:
            self[:]
        self._data[args] = value

    @property
    def data(self):
        return self[:]

    @data.setter
    def data(self, value):
        self.set_data(value)

    @property
    def shape(self):
        return self[:].shape

    @property
    def size(self):
        return self[:].size

    @property
    def dtype(self):
        return self[:].dtype


    def __eq__(self, other):
        self[:]

        if isinstance(other, self.__class__):
            if self.__dict__.keys() != other.__dict__.keys():
                return False

            for key in self.__dict__:
                if key == "_data":
                    if not np.array_equal(self.__dict__["_data"], other.__dict__["_data"]):
                        return False
                else:
                    if self.__dict__[key] != other.__dict__[key]:
                        return False
            return True
        else:
            return False

    def __len__(self):
         """ The size of the first axis.  TypeError if scalar."""
         if len(self.shape) == 0:
                raise TypeError("Attempt to take len() of scalar dataset")
         return self.shape[0]


    def __iter__(self):
        """Iterate over the first axis.  TypeError if scalar.
        WARNING: Modifications to the yielded data are *NOT* written to file.
        """

        if len(self.shape) == 0:
            raise TypeError("Can't iterate over a scalar dataset")

        for i in range(self.shape[0]):
            yield self[i]