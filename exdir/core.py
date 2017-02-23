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
from enum import Enum

# metadata
EXDIR_METANAME = "exdir"
TYPE_METANAME = "type"
VERSION_METANAME = "version"

# filenames
META_FILENAME = "meta.yml"
ATTRIBUTES_FILENAME = "attributes.yml"
RAW_FOLDER_NAME = "__raw__"

# typenames
DATASET_TYPENAME = "dataset"
GROUP_TYPENAME = "group"
FILE_TYPENAME = "file"


def convert_back_quantities(value):
    '''
    Converts quantities back from dictionary
    '''
    result = value
    if isinstance(value, dict):
        if "unit" in value and "value" in value and "uncertainty" in value:
            result = pq.UncertainQuantity(value["value"],
                                          value["unit"],
                                          value["uncertainty"])
        elif "unit" in value and "value" in value:
            result = pq.Quantity(value["value"], value["unit"])
        else:
            try:
                for key, value in result.items():
                    result[key] = convert_back_quantities(value)
            except AttributeError:
                pass

    return result


def convert_quantities(value):
    '''
    Converts quantities to dictionary
    '''
    result = value
    if isinstance(value, pq.Quantity):
        result = {
            "value": value.magnitude.tolist(),
            "unit": value.dimensionality.string
        }
        if isinstance(value, pq.UncertainQuantity):
            assert(value.dimensionality == value.uncertainty.dimensionality)
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


def _assert_valid_name(name):
    '''
    Check if name (dataset or group) is valid
    '''
    if len(name) < 1:
        raise NameError("Name cannot be empty.")

    valid_characters = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY" +
                        "Z1234567890_ ")

    for char in name:
        if char not in valid_characters:
            raise NameError("Name contains invalid character '" + char + "'.")

    invalid_names = [META_FILENAME,
                     ATTRIBUTES_FILENAME,
                     RAW_FOLDER_NAME]
    if name in invalid_names:
        raise NameError("Name cannot be '" + name + "'.")


def _create_object_directory(directory, typename):
    '''
    Create object directory and meta file if directory
    don't already exist
    '''
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


def _is_valid_object_directory(directory):
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


class OpenMode(Enum):
    read_write = 1
    read_only = 2


class Attribute:
    '''
    Attribute class.
    '''
    class Mode(Enum):
        attributes = 1
        metadata = 2

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

        if isinstance(name, np.integer):
            key = int(name)
        else:
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

    @property
    def dict(self):
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
        if self.io_mode == Object.OpenMode.read_only:
            raise IOError('Cannot write in read only ("r") mode')
        meta_data = convert_quantities(meta_data)
        with open(self.filename, "w") as meta_file:
            yaml.safe_dump(meta_data,
                           meta_file,
                           default_flow_style=False,
                           allow_unicode=True)

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
        if self.mode == self.Mode.metadata:
            return self.parent.meta_filename
        else:
            return self.parent.attributes_filename

    def __len__(self):
        return len(self.keys())


class Object(object):
    '''
    Parent class for exdir Group and exdir dataset objects
    '''
    class OpenMode(Enum):
        read_write = 1
        read_only = 2

    def __init__(self, root_directory, parent_path, object_name, io_mode=None):
        self.root_directory = root_directory
        self.object_name = object_name
        self.parent_path = parent_path
        if parent_path == "":
            self.relative_path = self.object_name
        else:
            self.relative_path = self.parent_path + "/" + self.object_name
        self.name = "/" + self.relative_path
        self.io_mode = io_mode

    @property
    def attrs(self):
        return Attribute(self, mode=Attribute.Mode.attributes,
                         io_mode=self.io_mode)

    @attrs.setter
    def attrs(self, value):
        self.attrs._set_data(value)

    @property
    def meta(self):
        return Attribute(self, mode=Attribute.Mode.metadata,
                         io_mode=self.io_mode)

    @property
    def directory(self):
        return os.path.join(self.root_directory,
                            self.relative_path.replace("/", os.sep))

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


class Group(Object):
    '''
    Container of other groups and datasets.
    '''
    def __init__(self, root_directory, parent_path, object_name, io_mode=None):
        super(Group, self).__init__(root_directory=root_directory,
                                    parent_path=parent_path,
                                    object_name=object_name, io_mode=io_mode)

    def create_dataset(self, name, data=None):
        _assert_valid_name(name)
        if name in self:
            raise IOError("An object with name '" + name + "' already exists.")

        dataset_directory = os.path.join(self.directory, name)
        _create_object_directory(dataset_directory, DATASET_TYPENAME)
        # TODO check dimensions, npy or npz
        dataset = Dataset(root_directory=self.root_directory,
                          parent_path=self.relative_path, object_name=name,
                          io_mode=self.io_mode)
        if data is not None:
            dataset.set_data(data)
        return dataset

    def create_group(self, name):
        _assert_valid_name(name)
        group_directory = os.path.join(self.directory, name)
        _create_object_directory(group_directory, GROUP_TYPENAME)
        group = Group(root_directory=self.root_directory,
                      parent_path=self.relative_path, object_name=name,
                      io_mode=self.io_mode)
        return group

    def require_group(self, name):
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
        parent = self.parent_path.split('/')[-1]
        parent_parent = "/".join(self.parent_path.split('/')[:-1])
        return Group(root_directory=self.root_directory,
                     parent_path=parent_parent, object_name=parent,
                     io_mode=self.io_mode)

    def require_dataset(self, name, data=None):
        if name in self:
            current_object = self[name]
            if isinstance(current_object, Dataset) and data is not None:
                current_object.set_data(data)
                return current_object
            elif isinstance(current_object, Dataset) and data is None:
                return current_object
            else:
                raise TypeError("An object with name '" + name + "' already "
                                "exists, but it is not a Group.")
        else:
            return self.create_dataset(name, data=data)

    def __contains__(self, name):
        if len(name) < 1:
            return False
        directory = os.path.join(self.directory, name)
        if _is_valid_object_directory(directory):
            return True
        else:
            return False

    def __getitem__(self, name):
        if "/" in name:
            if name[0] == '/':
                if isinstance(self, File):
                    name = name[1:]
                else:
                    raise KeyError('To begin tree structure with "/" is only' +
                                   ' allowed for get item from root object')
            name_split = name.split("/", 1)
            if len(name_split) == 2:
                item = self[name_split[0]]
                return item[name_split[1]]
            else:
                return self[name_split[0]]

        directory = os.path.join(self.directory, name)
        if name not in self:
            raise KeyError("No such object: '" + name + "'")

        if not _is_valid_object_directory(directory):
            raise IOError("Directory '" + directory +
                          "' is not a valid exdir object.")

        meta_filename = os.path.join(self.directory, name, META_FILENAME)
        with open(meta_filename, "r") as meta_file:
            meta_data = yaml.safe_load(meta_file)
        if meta_data[EXDIR_METANAME][TYPE_METANAME] == DATASET_TYPENAME:
            return Dataset(root_directory=self.root_directory,
                           parent_path=self.relative_path, object_name=name,
                           io_mode=self.io_mode)
        elif meta_data[EXDIR_METANAME][TYPE_METANAME] == GROUP_TYPENAME:
            return Group(root_directory=self.root_directory,
                         parent_path=self.relative_path, object_name=name,
                         io_mode=self.io_mode)
        else:
            print("Data type", meta_data[EXDIR_METANAME][TYPE_METANAME])
            raise NotImplementedError("Only dataset implemented")

    def __setitem__(self, name, value):
        if name not in self:
            self.create_dataset(name, value)
        else:
            current_item = self.__getitem__(name)
            if isinstance(current_item, Dataset):
                print("Is dataset")
            else:
                print("Data type")
                raise NotImplementedError("Only dataset writing implemented")

    def keys(self):
        for name in sorted(os.listdir(self.directory)):
            if name in self:
                yield name

    def items(self):
        for name in sorted(os.listdir(self.directory)):
            if name in self:
                yield name, self[name]

    def values(self):
        for name in sorted(os.listdir(self.directory)):
            if name in self:
                yield self[name]

    def __iter__(self):
        for name in sorted(os.listdir(self.directory)):
            if name in self:
                yield name


class File(Group):
    '''
    Exdir file object
    '''

    def __init__(self, directory, mode=None, allow_remove=False):
        if not directory.endswith('.exdir'):
            directory = directory + '.exdir'
        if mode is None:
            mode = "a"
        if mode == 'r':
            self.io_mode = self.OpenMode.read_only
        else:
            self.io_mode = self.OpenMode.read_write
        super(File, self).__init__(root_directory=directory,
                                   parent_path="", object_name="",
                                   io_mode=self.io_mode)

        already_exists = os.path.exists(directory)
        if already_exists:
            if not _is_valid_object_directory(directory):
                raise FileExistsError("Path '" + directory +
                                      "' already exists, but is not a valid " +
                                      "exdir object.")
            if self.meta[EXDIR_METANAME][TYPE_METANAME] != FILE_TYPENAME:
                raise FileExistsError("Path '" + directory +
                                      "' already exists, but is not a valid " +
                                      "exdir file.")

        should_create_directory = False

        if mode == "r":
            if not already_exists:
                raise IOError("Directory " + directory + " does not exist.")
        elif mode == "r+":
            if not already_exists:
                raise IOError("Directory " + directory + " does not exist.")
        elif mode == "w":
            if already_exists:
                if allow_remove:
                    shutil.rmtree(directory)
                else:
                    raise FileExistsError(
                        "File already exists. We won't delete the entire tree" +
                        " by default. Add allow_remove=True to override."
                    )
            should_create_directory = True
        elif mode == "w-" or mode == "x":
            if already_exists:
                raise IOError("Directory " + directory + " already exists.")
            should_create_directory = True
        elif mode == "a":
            if not already_exists:
                should_create_directory = True

        if should_create_directory:
            _create_object_directory(directory, FILE_TYPENAME)

    def close(self):
        # yeah right, as if we would create a real file format
        pass


class Dataset(Object):
    """
    Dataset class

    Warning: MODIFIES VIEW!!!!!!! different from h5py
    """
    def __init__(self, root_directory, parent_path, object_name, io_mode=None):
        super(Dataset, self).__init__(root_directory=root_directory,
                                      parent_path=parent_path,
                                      object_name=object_name,
                                      io_mode=io_mode)
        self.data_filename = os.path.join(self.directory, "data.npy")
        self._data = None
        if self.io_mode == self.OpenMode.read_only:
            self._mmap_mode = 'r'
        else:
            self._mmap_mode = 'r+'

    def set_data(self, data):
        if self.io_mode == self.OpenMode.read_only:
            raise IOError('Cannot write data to file in read only ("r") mode')
        if isinstance(data, pq.Quantity):
            result = data.magnitude
            self.attrs["unit"] = data.dimensionality.string
            if isinstance(data, pq.UncertainQuantity):
                self.attrs["uncertainty"] = data.uncertainty
        else:
            result = data
        if result is not None:
            if os.path.exists(self.data_filename):
                raise FileExistsError('Unable to create dataset "' +
                                      self.data_filename +
                                      '"(dataset already exists)')
            np.save(self.data_filename, result)

    def __getitem__(self, args):
        if not os.path.exists(self.data_filename):
            return np.array()
        if self._data is None:
            self._data = np.load(self.data_filename, mmap_mode=self._mmap_mode)
        if len(self._data.shape) == 0:
            return self._data
        else:
            return self._data[args]

    def __setitem__(self, args, value):
        if self.io_mode == self.OpenMode.read_only:
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
