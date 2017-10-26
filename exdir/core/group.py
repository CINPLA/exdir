import os
import re
import yaml
import pathlib
import numpy as np
import exdir
from collections import abc

from .exdir_object import Object
from . import exdir_object as exob
from . import dataset as ds
from . import raw
from .. import utils

def _data_to_shape_and_dtype(data, shape, dtype):
    if data is not None:
        if shape is None:
            shape = data.shape
        if dtype is None:
            dtype = data.dtype
        return shape, dtype
    if dtype is None:
        dtype = np.float32
    return shape, dtype

def _assert_data_shape_dtype_match(data, shape, dtype):
    if data is not None:
        if shape is not None and np.product(shape) != np.product(data.shape):
            raise ValueError(
                "Provided shape and data.shape do not match: {} vs {}".format(
                    shape, data.shape
                )
            )

        if dtype is not None and not data.dtype == dtype:
            raise ValueError(
                "Provided dtype and data.dtype do not match: {} vs {}".format(
                    dtype, data.dtype
                )
            )
        return

def _prepare_write(data):
    attrs = {}
    for plugin in exdir.dataset_plugins:
        plugin_attrs, data = plugin.prepare_write(data)
        attrs.update(plugin_attrs)

    if data is not None:
        data = np.asarray(data, order="C")

    return data, attrs

class Group(Object):
    """
    Container of other groups and datasets.
    """

    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 validate_name=None):
        super(Group, self).__init__(
            root_directory=root_directory,
            parent_path=parent_path,
            object_name=object_name, io_mode=io_mode,
            validate_name=validate_name
        )

    def create_dataset(self, name, shape=None, dtype=None,
                       data=None, fillvalue=None):
        exob._assert_valid_name(name, self)

        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError("Cannot write data to file in read only ('r') mode")

        if name in self:
            raise FileExistsError(
                "'{}' already exists in '{}'".format(name, self.name)
            )

        data, attrs = _prepare_write(data)

        _assert_data_shape_dtype_match(data, shape, dtype)
        if data is None and shape is None:
            raise TypeError(
                "Cannot create dataset. Missing shape or data keyword."
            )

        shape, dtype = _data_to_shape_and_dtype(data, shape, dtype)

        if data is not None:
            if shape is not None and data.shape != shape:
                data = np.reshape(data, shape)
        else:
            if shape is None:
                data = None
            else:
                fillvalue = fillvalue or 0.0
                data = np.full(shape, fillvalue, dtype=dtype)

        if data is None:
            raise TypeError("Could not create a meaningful dataset.")

        dataset_directory = self.directory / name

        exob._create_object_directory(dataset_directory, exob.DATASET_TYPENAME)

        dataset = self[name]
        dataset._reset(data, skip_plugins=True)
        dataset.attrs = attrs
        return dataset

    def create_group(self, name):
        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError("Cannot write data to file in read only ("r") mode")

        path = utils.path.name_to_asserted_group_path(name)
        if len(path.parts) > 1:
            subgroup = self.require_group(path.parent)
            subgroup.create_group(path.name)
            return

        exob._assert_valid_name(path, self)

        if name in self:
            raise FileExistsError(
                "'{}' already exists in '{}'".format(name, self.name)
            )

        group_directory = self.directory / path
        exob._create_object_directory(group_directory, exob.GROUP_TYPENAME)
        return self[name]

    def require_group(self, name):
        path = utils.path.name_to_asserted_group_path(name)
        if len(path.parts) > 1:
            subgroup = self.require_group(path.parent)
            return subgroup.require_group(path.name)

        group_directory = self.directory / name

        if name in self:
            current_object = self[name]
            if isinstance(current_object, Group):
                return current_object
            else:
                raise TypeError(
                    "An object with name '{}' already "
                    "exists, but it is not a Group.".format(name)
                )
        elif group_directory.exists():
            raise FileExistsError(
                "Directory " + group_directory + " already exists, " +
                "but is not an Exdir object."
            )

        return self.create_group(name)

    def require_dataset(self, name, shape=None, dtype=None, exact=False,
                        data=None, fillvalue=None):
        if name not in self:
            return self.create_dataset(
                name,
                shape=shape,
                dtype=dtype,
                data=data,
                fillvalue=fillvalue
            )

        current_object = self[name]

        if not isinstance(current_object, ds.Dataset):
            raise TypeError(
                "Incompatible object already exists: {}".format(
                    current_object.__class__.__name__
                )
            )

        data, attrs = _prepare_write(data)

        # TODO verify proper attributes

        _assert_data_shape_dtype_match(data, shape, dtype)
        shape, dtype = _data_to_shape_and_dtype(data, shape, dtype)

        if not np.array_equal(shape, current_object.shape):
            raise TypeError(
                "Shapes do not match (existing {} vs "
                "new {})".format(current_object.shape, shape)
            )

        if dtype != current_object.dtype:
            if exact:
                raise TypeError(
                    "Datatypes do not exactly match "
                    "existing {} vs new {})".format(current_object.dtype, dtype)
                )

            if not np.can_cast(dtype, current_object.dtype):
                raise TypeError(
                    "Cannot safely cast from {} to {}".format(
                        dtype,
                        current_object.dtype
                    )
                )

        return current_object

    def __contains__(self, name):
        if name == ".":
            return True
        if name == "":
            return False
        path = utils.path.name_to_asserted_group_path(name)
        directory = self.directory / path
        return exob.is_exdir_object(directory)

    def __getitem__(self, name):
        path = utils.path.name_to_asserted_group_path(name)
        if len(path.parts) > 1:
            top_directory = path.parts[0]
            sub_name = pathlib.PurePosixPath(*path.parts[1:])
            return self[top_directory][sub_name]

        if name not in self:
            raise KeyError("No such object: '" + str(name) + "'")

        directory = self.directory / path

        if exob.is_raw_object_directory(directory):  # TODO create one function that handles all Raw creation
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

        meta_filename = directory / exob.META_FILENAME
        with meta_filename.open("r", encoding="utf-8") as meta_file:
            meta_data = yaml.safe_load(meta_file)
        if meta_data[exob.EXDIR_METANAME][exob.TYPE_METANAME] == exob.DATASET_TYPENAME:
            return ds.Dataset(
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
        path = utils.path.name_to_asserted_group_path(name)
        if len(path.parts) > 1:
            self[path.parent][path.name] = value
            return

        if name not in self:
            self.create_dataset(name, data=value)
            return

        if not isinstance(self[name], ds.Dataset):
            raise RuntimeError(
                "Unable to assign value, {} already exists".format(name)
            )

        self[name].value = value

    def keys(self):
        return abc.KeysView(self)

    def items(self):
        return abc.ItemsView(self)

    def values(self):
        return abc.ValuesView(self)

    def __iter__(self):
        # NOTE os.walk is way faster than os.listdir + os.path.isdir
        directories = next(os.walk(str(self.directory)))[1]
        for name in sorted(directories):
            yield name
