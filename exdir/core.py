from __future__ import print_function, division, unicode_literals

import os
import yaml
import numpy as np
import shutil
from enum import Enum


META_FILENAME = "meta.yml"
ATTRIBUTES_FILENAME = "attributes.yml"
RAW_FOLDER_NAME = "__raw__"
DATASET_TYPENAME = "Dataset"
GROUP_TYPENAME = "Group"
FILE_TYPENAME = "File"


def _assert_valid_name(name):
    if len(name) < 1:
        raise NameError("Name cannot be empty.")
        
    valid_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_"
    
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
        yaml.dump({"type": typename, "exdir_version": 1},
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
        if "type" not in meta_data:
            return False
        valid_types = [DATASET_TYPENAME, FILE_TYPENAME, GROUP_TYPENAME]
        if meta_data["type"] not in valid_types:
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
        with open(self.filename, "r") as meta_file:
            meta_data = yaml.load(meta_file)
        return meta_data[name]
        
    def __setitem__(self, name, value):        
        meta_data = {}
        # TODO consider failing or warning on missing yaml
        if os.path.exists(self.filename):
            with open(self.filename, "r") as meta_file:
                meta_data = yaml.load(meta_file)
        
        meta_data[name] = value
        print(value)
        self._set_data(meta_data)
        
    def _set_data(self, meta_data):
        with open(self.filename, "w") as meta_file:
            yaml.dump(meta_data,
                      meta_file,
                      default_flow_style=False,
                      allow_unicode=True)
                      
    @property
    def filename(self):
        if self.mode == self.Mode.metadata:            
            return self.parent.meta_filename
        else:
            return self.parent.attributes_filename


class Object(object):
    def __init__(self, parent, name, mode=None):
        if mode is None:
            if parent is None:
                raise AttributeError("Both 'mode' and 'parent' cannot be None.")
            mode = parent.mode
        self.parent = parent
        self.name = name
        self.mode = mode

    @property   
    def attrs(self):
        return AttributeManager(self, AttributeManager.Mode.attributes)
        
    @attrs.setter
    def attrs(self, value):
        manager = self.attrs
        manager._set_data(value)
    
    @property
    def meta(self):
        return AttributeManager(self, AttributeManager.Mode.metadata)
        
    @property
    def folder(self):
        if self.parent is not None:
            return os.path.join(self.parent.folder, self.name)
        else:
            return self.root_folder
        
    @property
    def attributes_filename(self):
        return os.path.join(self.folder, ATTRIBUTES_FILENAME)
    
    @property
    def meta_filename(self):
        return _metafile_from_folder(self.folder)


class Group(Object):
    def __init__(self, parent, name, mode=None):
        super(Group, self).__init__(parent=parent, name=name, mode=mode)
        
    def create_dataset(self, name, data=None):
        _assert_valid_name(name)
        if name in self:
            raise IOError("An object with name '" + name + "' already exists.")
            
        dataset_folder = os.path.join(self.folder, name)
        _create_object_folder(dataset_folder, DATASET_TYPENAME)
        # TODO check dimensions, npy or npz
        dataset = Dataset(parent=self, name=name)
        if data is not None:
            dataset.set_data(data)
        return dataset
        
    def create_group(self, name):
        _assert_valid_name(name)
        group_folder = os.path.join(self.folder, name)
        _create_object_folder(group_folder, GROUP_TYPENAME)
        group = Group(parent=self, name=name)
        return group
        
    def require_group(self, name):
        if name in self:
            current_object = self[name]
            if isinstance(current_object, Group):
                return current_object
            else:
                raise TypeError("An object with name '" + name + "' already "
                                "exists, but it is not a Group.")
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
        folder = os.path.join(self.folder, name)
        if os.path.exists(folder):
            return True
        else:
            return False
        
    def __getitem__(self, name):
        # TODO support relative paths
        folder = os.path.join(self.folder, name)
        if name not in self:
            raise KeyError("No such object: '" + name + "'")
        
        if not _is_valid_object_folder(folder):
            raise IOError("Folder '" + folder + "' is not a valid exdir object.")
        
        meta_filename = os.path.join(self.folder, name, META_FILENAME)
        with open(meta_filename, "r") as meta_file:
            meta_data = yaml.load(meta_file)
        if meta_data["type"] == DATASET_TYPENAME:
            return Dataset(self, name)
        elif meta_data["type"] == GROUP_TYPENAME:
            return Group(self, name)
        else:
            print("Data type", meta_data["type"])
            raise NotImplementedError("Only dataset implemented")
    
    def __setitem__(self, name, value):
        if name not in self:
            create_dataset(name, value)
        else:
            current_item = self.__getitem__(name)
            if isinstance(current_item, Dataset):
                print("Is dataset")
            else:
                print("Data type")
                raise NotImplementedError("Only dataset writing implemented")


class File(Group):
    def __init__(self, folder, mode=None):
        if mode is None:
            mode = "a"
        super(File, self).__init__(parent=None, name="__root__", mode=mode)
        self.root_folder = folder
        
        already_exists = os.path.exists(folder)
        if already_exists:
            if not _is_valid_object_folder(folder):
                raise FileExistsError("Path '" + folder + "' already exists, but is not a valid exdir object.")
            if self.meta["type"] != "File":
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
                shutil.rmtree(folder)
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
    def __init__(self, parent, name, mode=None):
        super(Dataset, self).__init__(parent=parent, name=name, mode=mode)
        self.data_filename = os.path.join(self.folder, "data.npy")
    
    def set_data(self, data):
        np.save(self.data_filename, data)
        
    def __getitem__(self, args):        
        data = np.load(self.data_filename)
        return data[args]
        
    def __setitem__(self, args, value):
        data = np.load(self.data_filename)
        data[args] = value
        np.save(self.data_filename, data)
        
    @property
    def data(self):
        return self[:]
