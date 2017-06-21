import os
import re
import yaml
import pathlib
import numpy as np
from collections import abc

from .exdir_object import Object
from . import exdir_object as exob
from .dataset import Dataset
from . import raw


def _name_to_path(name):
    if name.startswith("/"):
        raise NotImplementedError(
            "Getting a group in the root directory " +
            "from a subgroup is currently not supported " +
            "and is unlikely to be implemented."
        )

    path = pathlib.PurePosixPath(name)

    if len(path.parts) < 1:
        raise NotImplementedError(
            "Getting an item on a group with path '" + name + "' " +
            "is not supported and unlikely to be implemented."
        )
        
    return path


class Group(Object):
    """
    Container of other groups and datasets.
    """

    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 validate_name=None):
        super(Group, self).__init__(root_directory=root_directory,
                                    parent_path=parent_path,
                                    object_name=object_name, io_mode=io_mode,
                                    validate_name=validate_name)

    def create_dataset(self, name, shape=None, dtype=None,
                       data=None, fillvalue=None):
        exob._assert_valid_name(name, self)
        dataset_directory = os.path.join(self.directory, name)
        exob._create_object_directory(dataset_directory, exob.DATASET_TYPENAME)
        # TODO check dimensions, npy or npz
        dataset = Dataset(root_directory=self.root_directory,
                          parent_path=self.relative_path, object_name=name,
                          io_mode=self.io_mode,
                          validate_name=self.validate_name)

        dataset.set_data(shape=shape, dtype=dtype, data=data, fillvalue=fillvalue)

        return dataset

    def create_group(self, name):
        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError("Cannot write data to file in read only ("r") mode")

        path = _name_to_path(name)

        if len(path.parts) > 1:
            raise NotImplementedError("Intermediate groups can not yet be " +
                                      "created automatically.")

        exob._assert_valid_name(str(path), self)
        group_directory = self.directory / path
        exob._create_object_directory(group_directory, exob.GROUP_TYPENAME)
        group = Group(root_directory=self.root_directory,
                      parent_path=self.relative_path, object_name=name,
                      io_mode=self.io_mode,
                      validate_name=self.validate_name)
        return group

    def require_group(self, name):
        path = _name_to_path(name)
        group_directory = self.directory / path
        
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
                current_object.set_data(shape=shape, dtype=dtype,
                                        data=data, fillvalue=fillvalue)
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

        return exob.is_exdir_object(directory)

    def __getitem__(self, name):
        path = _name_to_path(name)

        if len(path.parts) > 1:
            if len(path.parts) == 2:
                item = self[path.parts[0]]
                return item[path.parts[1]]
            else:
                return self[path.parts[0]]
                
        if name not in self:
            raise KeyError("No such object: '" + name + "'")

        directory = os.path.join(self.directory, path)

        if exob.is_raw_object_directory(directory):
            return raw.Raw(
                root_directory=self.root_directory,
                parent_path=self.relative_path,
                object_name=name,
                io_mode=self.io_mode # TODO validate name?
            )

        if not exob.is_nonraw_object_directory(directory):
            raise IOError(
                "Directory '" + directory +
                "' is not a valid exdir object."
            )

        meta_filename = os.path.join(self.directory, path, exob.META_FILENAME)
        with open(meta_filename, "r") as meta_file:
            meta_data = yaml.safe_load(meta_file)
        if meta_data[exob.EXDIR_METANAME][exob.TYPE_METANAME] == exob.DATASET_TYPENAME:
            return Dataset(
                root_directory=self.root_directory,
                parent_path=self.relative_path,
                object_name=name,
                io_mode=self.io_mode,
                validate_name=self.validate_name
            )
        elif meta_data[exob.EXDIR_METANAME][exob.TYPE_METANAME] == exob.GROUP_TYPENAME:
            return Group(
                root_directory=self.root_directory,
                parent_path=self.relative_path,
                object_name=name,
                io_mode=self.io_mode,
                validate_name=self.validate_name
            )
        else:
            print(
                "Object", name, "has data type",
                meta_data[exob.EXDIR_METANAME][exob.TYPE_METANAME]
            )
            raise NotImplementedError("Cannot open objects of this type")

    def __setitem__(self, name, value):
        if name not in self:
            self.create_dataset(name, data=value)
        else:
            # TODO overwrite or not?
            raise RuntimeError("Unable to assign value, {} already exists".format(name))

            # current_item = self.__getitem__(name)
            # if isinstance(current_item, Dataset):
            #     current_item.set_data(data=value)
            # else:
            #     print("Data type")
            #     raise NotImplementedError("Only dataset writing implemented")

    def keys(self):
        return abc.KeysView(self)

    def items(self):
        return abc.ItemsView(self)

    def values(self):
        return abc.ValuesView(self)

    def __iter__(self):
        # NOTE os.walk is way faster than os.listdir + os.path.isdir
        directories = next(os.walk(self.directory))[1]
        for name in sorted(directories):
            yield name
