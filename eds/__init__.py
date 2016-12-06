import os
import yaml
import numpy as np

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

class Base:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        print("Base constructor")
        pass

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
        return os.path.join(self.folder, "meta.yml")


class Group(Base):
    def __init__(self, parent, name):
        super(Group, self).__init__(parent, name)
        
    def create_dataset(self, name, data):
        dataset_folder = os.path.join(self.folder, name)
        if os.path.exists(dataset_folder):
            raise IOError("A dataset with the name " + name + "already exists")
        os.mkdir(dataset_folder)
        # TODO check dimensions, npy or npz
        dataset = Dataset(self, name)
        
        with open(dataset.meta_filename, "w") as meta_file:
            yaml.dump({"type": "dataset"},
                      meta_file,
                      default_flow_style=False,
                      allow_unicode=True)
                      
        dataset._write(data)
        return dataset
        
    def __getitem__(self, name):
        folder = os.path.join(self.folder, name)
        meta_filename = os.path.join(self.folder, name, "meta.yml")
        with open(meta_filename, "r") as meta_file:
            meta_data = yaml.load(meta_file)
        if meta_data["type"] == "dataset":
            return Dataset(self, name)
        else:
            print("Data type", meta_data["type"])
            raise NotImplementedError("Only dataset implemented")


class File(Group):
    def __init__(self, folder, mode=None):
        super(File, self).__init__(None, "__root__")
        self.root_folder = folder
        print("Opening", folder)
        if mode is None:
            mode = "a"
            
        if mode == "r":
            # TODO open folder if exists, otherwise fail
            pass
        elif mode == "r+":
            # TODO open folder if exists, otherwise fail
            pass
        elif mode == "w":
            # TODO create folder or trunc if exists
            pass
        elif mode == "w-" or mode == "x":
            # TODO create file, fail if exists
            pass
        elif mode == "a":
            # TODO read/write if exists, create if doesn't exist
            if os.path.exists(folder):
                # TODO read folder structure and meta.yml
                # TODO if meta.yml is missing, raise exception
                pass
            else:
                # TODO create folder and meta.yml
                os.mkdir(folder)
                
            with open(self.meta_filename, "w") as eds_config_file:
                yaml.dump({"eds_version": 1, "type": "file"}, 
                          eds_config_file,
                          default_flow_style=False,
                          allow_unicode=True)
                          

class Dataset(Base):
    def __init__(self, parent, name):
        super(Dataset, self).__init__(parent, name)
        self.data_filename = os.path.join(self.folder, "data.npy")
    
    def _write(self, data):
        np.save(self.data_filename, data)
        
    def __getitem__(self, args):        
        data = np.load(self.data_filename)
        return data[args]
        
    @property
    def data(self):
        return self[:]

if __name__ == "__main__":
    import shutil
    testfile = "/tmp/test.eds"
    if os.path.exists(testfile):
        shutil.rmtree(testfile)
    f = File(testfile)
    f.attrs["temperature"] = 99.0
    print(f.attrs["temperature"])
    
    a = np.array([1, 2, 3, 4])
    dset = f.create_dataset("mydata", a)
    
    print(dset.data)
    
    print(f["mydata"][2])
    
    # TODO add dataset
