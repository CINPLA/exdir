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


def _assert_valid_name(name):
    if len(name) < 1:
        raise NameError("Name cannot be empty.")

    valid_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_ "

    for char in name:
        if char not in valid_characters:
            raise NameError("Name contains invalid character '" + char + "'.")

    invalid_names = [META_FILENAME,
                     ATTRIBUTES_FILENAME,
                     RAW_FOLDER_NAME]
    if name in invalid_names:
        raise NameError("Name cannot be '" + name + "'.")


def _create_object_folder(folder, typename):
    if os.path.exists(folder):
        raise IOError("The folder '" + folder + "' already exists")
    os.mkdir(folder)
    meta_filename = _metafile_from_folder(folder)
    with open(meta_filename, "w") as meta_file:
        metadata = {
            EXDIR_METANAME: {
                TYPE_METANAME: typename,
                VERSION_METANAME: 1}
        }
        yaml.dump(metadata,
                  meta_file,
                  default_flow_style=False,
                  allow_unicode=True)


def _metafile_from_folder(folder):
    return os.path.join(folder, META_FILENAME)


def _is_valid_object_folder(folder):
    meta_filename = os.path.join(folder, META_FILENAME)
    if not os.path.exists(meta_filename):
        return False
    with open(meta_filename, "r") as meta_file:
        meta_data = yaml.load(meta_file)
        if EXDIR_METANAME not in meta_data:
            return False
        if TYPE_METANAME not in meta_data[EXDIR_METANAME]:
            return False
        valid_types = [DATASET_TYPENAME, FILE_TYPENAME, GROUP_TYPENAME]
        if meta_data[EXDIR_METANAME][TYPE_METANAME] not in valid_types:
            return False
    return True


class AttributeManager:
    class Mode(Enum):
        attributes = 1
        metadata = 2

    def __init__(self, parent, mode):
        self.parent = parent
        self.mode = mode

    def __getitem__(self, name):
        # TODO return new AttributeManager with subpath
        meta_data = self._open_or_create()
        return meta_data[name]

    def __setitem__(self, name, value):
        meta_data = self._open_or_create()

        if isinstance(value, pq.Quantity):
            result = {
                "value": value.magnitude.tolist(),
                "unit": value.dimensionality.string
            }
            if isinstance(value, pq.UncertainQuantity):
                result["uncertainty"] = value.uncertainty
        elif isinstance(value, np.ndarray):
            result = value.tolist()
        elif isinstance(value, np.integer):
            result = int(value)
        else:
            result = value
        if isinstance(name, np.integer):
            key = int(name)
        else:
            key = name
        meta_data[key] = result
        self._set_data(meta_data)
    
    def __contains__(self, name):
        meta_data = self._open_or_create()
        return name in meta_data

    def keys(self):
        meta_data = self._open_or_create()
        return meta_data.keys()

    def items(self):
        meta_data = self._open_or_create()
        return meta_data.items()

    def values(self):
        meta_data = self._open_or_create()
        return meta_data.values()

    def _set_data(self, meta_data):
        with open(self.filename, "w") as meta_file:
            yaml.dump(meta_data,
                      meta_file,
                      default_flow_style=False,
                      allow_unicode=True)

    def _open_or_create(self):
        meta_data = {}
        if os.path.exists(self.filename):
            with open(self.filename, "r") as meta_file:
                meta_data = yaml.load(meta_file)
        return meta_data

    @property
    def filename(self):
        if self.mode == self.Mode.metadata:
            return self.parent.meta_filename
        else:
            return self.parent.attributes_filename


class Object(object):
    def __init__(self, root_folder, parent_path, object_name, mode=None):
        # TODO: use mode
        self.root_folder = root_folder
        self.object_name = object_name
        self.parent_path = parent_path
        if parent_path == "":
            self.relative_path = self.object_name
        else:
            self.relative_path = self.parent_path + "/" + self.object_name
        self.name = "/" + self.relative_path
        self.mode = mode

    @property
    def attrs(self):
        meta_data = {}
        if os.path.exists(self.attributes_filename):
            with open(self.attributes_filename, "r") as meta_file:
                meta_data = yaml.load(meta_file)
        if meta_data:
            self.convert_back_quantities(meta_data)
        return meta_data or {}
        # return AttributeManager(self, AttributeManager.Mode.attributes)

    def convert_back_quantities(self, value):
        to_ret = value
        if isinstance(value, dict):
            if "unit" in value and "value" in value:
                to_ret = pq.Quantity(value["value"], value["unit"])
            else:
                try:
                    for key, value in to_ret.items():
                        to_ret[key] = self.convert_back_quantities(value)
                except AttributeError:
                    pass

        return to_ret

    def convert_quantities(self, value):
        to_ret = value
        if isinstance(value, pq.Quantity):
            to_ret = {
                "value": value.magnitude.tolist(),
                "unit": value.dimensionality.string
            }
            if isinstance(value, pq.UncertainQuantity):
                to_ret["uncertainty"] = value.uncertainty
        else:
            try:
                for key, value in to_ret.items():
                    to_ret[key] = self.convert_quantities(value)
            except AttributeError:
                pass

        return to_ret

    @attrs.setter
    def attrs(self, value):
        self.convert_quantities(value)
        with open(self.attributes_filename, "w") as meta_file:
            yaml.dump(value,
                      meta_file,
                      default_flow_style=False,
                      allow_unicode=True)
        # manager = self.attrs
        # manager._set_data(value)

    @property
    def meta(self):
        return AttributeManager(self, AttributeManager.Mode.metadata)

    @property
    def folder(self):
        return os.path.join(self.root_folder, self.relative_path.replace("/", os.sep))

    @property
    def attributes_filename(self):
        return os.path.join(self.folder, ATTRIBUTES_FILENAME)

    @property
    def meta_filename(self):
        return _metafile_from_folder(self.folder)
        
    def create_raw(self, name):
        folder_name = os.path.join(self.folder, name)
        if os.path.exists(folder_name):
            raise IOError("Raw folder " + folder_name + " already exists.")
        os.mkdir(folder_name)
        return folder_name
        
    def require_raw(self, name):
        folder_name = os.path.join(self.folder, name)
        if os.path.exists(folder_name):
            return folder_name
        else:
            return self.create_raw(name)


class Group(Object):
    def __init__(self, root_folder, parent_path, object_name, mode=None):
        super(Group, self).__init__(root_folder=root_folder, parent_path=parent_path, object_name=object_name, mode=mode)

    def create_dataset(self, name, data=None):
        _assert_valid_name(name)
        if name in self:
            raise IOError("An object with name '" + name + "' already exists.")

        dataset_folder = os.path.join(self.folder, name)
        _create_object_folder(dataset_folder, DATASET_TYPENAME)
        # TODO check dimensions, npy or npz
        dataset = Dataset(root_folder=self.root_folder, parent_path=self.relative_path, object_name=name)
        if data is not None:
            dataset.set_data(data)
        return dataset

    def create_group(self, name):
        _assert_valid_name(name)
        group_folder = os.path.join(self.folder, name)
        _create_object_folder(group_folder, GROUP_TYPENAME)
        group = Group(root_folder=self.root_folder, parent_path=self.relative_path, object_name=name)
        return group

    def require_group(self, name):
        group_folder = os.path.join(self.folder, name)
        if name in self:
            current_object = self[name]
            if isinstance(current_object, Group):
                return current_object
            else:
                raise TypeError("An object with name '" + name + "' already " +
                                "exists, but it is not a Group.")
        elif os.path.exists(group_folder):
            raise IOError("Folder " + group_folder + " already exists, " +
                          "but is not an Exdir object.")
        else:
            return self.create_group(name)

    def require_dataset(self, name, data=None):
        if name in self:
            current_object = self[name]
            if isinstance(current_object, Dataset):
                current_object.set_data(data)
                return current_object
            else:
                raise TypeError("An object with name '" + name + "' already "
                                "exists, but it is not a Group.")
        else:
            return self.create_dataset(name, data=data)

    def __contains__(self, name):
        if len(name) < 1:
            return False
        folder = os.path.join(self.folder, name)
        if _is_valid_object_folder(folder):
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
                
            

        folder = os.path.join(self.folder, name)
        if name not in self:
            raise KeyError("No such object: '" + name + "'")

        if not _is_valid_object_folder(folder):
            raise IOError("Folder '" + folder + "' is not a valid exdir object.")

        meta_filename = os.path.join(self.folder, name, META_FILENAME)
        with open(meta_filename, "r") as meta_file:
            meta_data = yaml.load(meta_file)
        if meta_data[EXDIR_METANAME][TYPE_METANAME] == DATASET_TYPENAME:
            return Dataset(root_folder=self.root_folder, parent_path= self.relative_path, object_name=name)
        elif meta_data[EXDIR_METANAME][TYPE_METANAME] == GROUP_TYPENAME:
            return Group(root_folder=self.root_folder, parent_path= self.relative_path, object_name=name)
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
        for name in sorted(os.listdir(self.folder)):
            if name in self:
                yield name

    def items(self):
        for name in sorted(os.listdir(self.folder)):
            if name in self:
                yield name, self[name]

    def values(self):
        for name in sorted(os.listdir(self.folder)):
            if name in self:
                yield self[name]

    def __iter__(self):
        for name in sorted(os.listdir(self.folder)):
            if name in self:
                yield name



class File(Group):
    def __init__(self, folder, mode=None, allow_remove=False):
        if mode is None:
            mode = "a"
        super(File, self).__init__(root_folder=folder, parent_path="", object_name="", mode=mode)

        already_exists = os.path.exists(folder)
        if already_exists:
            if not _is_valid_object_folder(folder):
                raise FileExistsError("Path '" + folder + "' already exists, but is not a valid exdir object.")
            if self.meta[EXDIR_METANAME][TYPE_METANAME] != FILE_TYPENAME:
                raise FileExistsError("Path '" + folder + "' already exists, but is not a valid exdir file.")

        should_create_folder = False

        if mode == "r":
            if not already_exists:
                raise IOError("Folder " + folder + " does not exist.")
        elif mode == "r+":
            if not already_exists:
                raise IOError("Folder " + folder + " does not exist.")
        elif mode == "w":
            if already_exists:
                if allow_remove:
                    shutil.rmtree(folder)
                else:
                    raise FileExistsError(
                        "File already exists. We won't delete the entire tree " +
                        "by default. Add allow_remove=True to override."
                    )
            should_create_folder = True
        elif mode == "w-" or mode == "x":
            if already_exists:
                raise IOError("Folder " + folder + " already exists.")
            should_create_folder = True
        elif mode == "a":
            if not already_exists:
                should_create_folder = True

        if should_create_folder:
            _create_object_folder(folder, FILE_TYPENAME)

    def close(self):
        # yeah right, as if we would create a real file format
        pass


class Dataset(Object):
    def __init__(self, root_folder, parent_path, object_name, mode=None):
        super(Dataset, self).__init__(root_folder=root_folder, parent_path=parent_path, object_name=object_name, mode=mode)
        self.data_filename = os.path.join(self.folder, "data.npy")

    def set_data(self, data):
        if isinstance(data, pq.Quantity):
            result = data.magnitude
            self.attrs["unit"] = data.dimensionality.string
            if isinstance(data, pq.UncertainQuantity):
                self.attrs["uncertainty"] = data.uncertainty
        else:
            result = data
        np.save(self.data_filename, result)


    def __getitem__(self, args):
        data = np.load(self.data_filename)
        if len(data.shape) == 0:
            return data
        else:
            return data[args]


    def __setitem__(self, args, value):
        data = np.load(self.data_filename)
        data[args] = value
        np.save(self.data_filename, data)

    @property
    def data(self):
        return self[:]
