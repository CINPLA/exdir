from __future__ import print_function, division, unicode_literals

import os
import yaml
import numpy as np


def _create_object_folder(folder, typename):
    if os.path.exists(folder):
        raise IOError("The folder '" + folder + "' already exists")
    os.mkdir(folder)
    meta_filename = _metafile_from_folder(folder)
    with open(meta_filename, "w") as meta_file:
        yaml.dump({"type": typename, "eds_version": 1},
                  meta_file,
                  default_flow_style=False,
                  allow_unicode=True)


def _metafile_from_folder(folder):
    return os.path.join(folder, "meta.yml")


class AttributeManager:
    def __init__(self, parent):
        self.parent = parent

    def __getitem__(self, name):
        with open(self.attributes_filename, "r") as meta_file:
            meta_data = yaml.load(meta_file)
        return meta_data[name]
        
    def __setitem__(self, name, value):
        meta_data = {}
        # TODO consider failing or warning on missing yaml
        if os.path.exists(self.attributes_filename):
            with open(self.attributes_filename, "r") as meta_file:
                meta_data = yaml.load(meta_file)
        
        meta_data[name] = value
        with open(self.attributes_filename, "w") as meta_file:
            yaml.dump(meta_data,
                      meta_file,
                      default_flow_style=False,
                      allow_unicode=True)
    
    @property
    def attributes_filename(self):
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
        return AttributeManager(self)
        
    @property
    def folder(self):
        if self.parent is not None:
            return os.path.join(self.parent.folder, self.name)
        else:
            return self.root_folder
        
    @property
    def attributes_filename(self):
        return os.path.join(self.folder, "attributes.yml")
    
    @property
    def meta_filename(self):
        return _metafile_from_folder(self.folder)


class Group(Object):
    def __init__(self, parent, name, mode=None):
        super(Group, self).__init__(parent=parent, name=name, mode=mode)
        
    def create_dataset(self, name, data=None):
        if name in self:
            raise IOError("An object with name '" + name + "' already exists.")
            
        dataset_folder = os.path.join(self.folder, name)
        _create_object_folder(dataset_folder, "dataset")
        # TODO check dimensions, npy or npz
        dataset = Dataset(parent=self, name=name)
        if data is not None:
            dataset.set_data(data)
        return dataset
        
    def create_group(self, name):
        group_folder = os.path.join(self.folder, name)
        _create_object_folder(group_folder, "group")
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
        folder = os.path.join(self.folder, name)
        meta_filename = os.path.join(self.folder, name, "meta.yml")
        with open(meta_filename, "r") as meta_file:
            meta_data = yaml.load(meta_file)
        if meta_data["type"] == "dataset":
            return Dataset(self, name)
        elif meta_data["type"] == "group":
            return Group(self, name)
        else:
            print("Data type", meta_data["type"])
            raise NotImplementedError("Only dataset implemented")
    
    def __setitem__(self, name, value):
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
        should_create_folder = False
        
        if mode == "r":
            if not already_exists:
                raise IOError("Folder " + folder + " does not exist.")
        elif mode == "r+":
            if not already_exists:
                raise IOError("Folder " + folder + " does not exist.")
        elif mode == "w":
            if already_exists:
                raise NotImplementedError("Should remove folder, not implemented. Please remove manually.")
            should_create_folder = True
        elif mode == "w-" or mode == "x":
            if already_exists:
                raise IOError("Folder " + folder + " already exists.")
            should_create_folder = True
        elif mode == "a":
            should_create_folder = True
        
        if should_create_folder and not already_exists:
            _create_object_folder(folder, "file")
                          

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

if __name__ == "__main__":
    import shutil
    testfile = "/tmp/test.eds"
    # if os.path.exists(testfile):
    #     shutil.rmtree(testfile)
    f = File(testfile)
    f.attrs["temperature"] = 99.0
    print(f.attrs["temperature"])
    
    a = np.array([1, 2, 3, 4, 5])
    dset = f.require_dataset("mydata", data=a)
    
    dset[1:3] = 8.0
    
    print(f["mydata"][()])
    
    print(f["mydata"][2])
    
    group = f.require_group("mygroup")
    
    b = np.array([[1, 2, 3], [4, 5, 6]])
    if "some_data" not in group:
        dset2 = group.create_dataset("some_data", b)
    else:
        group["some_data"] = b
        
    print(group["some_data"][()])
