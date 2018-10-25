import os
import re
import ruamel_yaml as yaml
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

class Group(Object):
    """
    Container of other groups and datasets.
    """

    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 name_validation=None, plugin_manager=None):
        """
        WARNING: Internal. Should only be called from require_group.
        """
        super(Group, self).__init__(
            root_directory=root_directory,
            parent_path=parent_path,
            object_name=object_name,
            io_mode=io_mode,
            name_validation=name_validation,
            plugin_manager=plugin_manager
        )

    def create_dataset(self, name, shape=None, dtype=None,
                       data=None, fillvalue=None):
        """
        Create a dataset. This will create a folder on the filesystem with the given
        name, an exdir.yaml file that identifies the folder as an Exdir Dataset,
        and a data.npy file that contains the data.

        Parameters
        ----------
        name: str
            Name of the dataset to be created.
        shape: tuple, semi-optional
            Shape of the dataset to be created.
            Must be set together with dtype.
            Cannot be set together with `data`, but must be set if `data` is not set.
        dtype: numpy.dtype
            Data type of the dataset to be created.
            Must be set together with `shape`.
            Cannot be set together with `data`, but must be set if `data` is not set.
        data: scalar, list, numpy.array or plugin-supported type, semi-optional
            Data to be inserted in the created dataset.
            Cannot be set together with `dtype` or `shape`, but must be set if
            `dtype` and `shape` are not set.
        fillvalue: scalar
            Used to create a dataset with the given `shape` and `type` with the
            initial value of `fillvalue`.

        Returns
        -------
        The newly created Dataset.

        Raises
        ------
        FileExistsError
            If an object with the same `name` already exists.

        See also
        --------
        require_dataset
        """
        exob._assert_valid_name(name, self)

        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError("Cannot write data to file in read only ('r') mode")

        exob._assert_valid_name(name, self)

        if data is None and shape is None:
            raise TypeError(
                "Cannot create dataset. Missing shape or data keyword."
            )

        prepared_data, attrs, meta = ds._prepare_write(data, self.plugin_manager.dataset_plugins.write_order)

        _assert_data_shape_dtype_match(prepared_data, shape, dtype)

        shape, dtype = _data_to_shape_and_dtype(prepared_data, shape, dtype)

        if prepared_data is not None:
            if shape is not None and prepared_data.shape != shape:
                prepared_data = np.reshape(prepared_data, shape)
        else:
            if shape is None:
                prepared_data = None
            else:
                fillvalue = fillvalue or 0.0
                prepared_data = np.full(shape, fillvalue, dtype=dtype)

        if prepared_data is None:
            raise TypeError("Could not create a meaningful dataset.")

        dataset_directory = self.directory / name
        exob._create_object_directory(dataset_directory, exob.DATASET_TYPENAME)

        dataset = self._dataset(name)
        dataset._reset_data(prepared_data, attrs, meta)
        return dataset

    def create_group(self, name):
        """
        Create a group. This will create a folder on the filesystem with the
        given name and an exdir.yaml file that identifies the folder as a
        group. A group can contain multiple groups and datasets.

        Parameters
        ----------
        name: str
            Name of the subgroup. Must follow the naming convention of the parent Exdir File.

        Raises
        ------
        FileExistsError
            If an object with the same `name` already exists.

        Returns
        -------
        The newly created Group.

        See also
        --------
        require_group
        """
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
        return self._group(name)

    def _group(self, name):
        return Group(
            root_directory=self.root_directory,
            parent_path=self.relative_path,
            object_name=name,
            io_mode=self.io_mode,
            name_validation=self.name_validation,
            plugin_manager=self.plugin_manager
        )

    def require_group(self, name):
        """
        Open an existing subgroup or create if it does not exist.
        This might create a new subfolder on the file system.

        Parameters
        ----------
        name: str
            Name of the subgroup. Must follow the naming convention of the parent Exdir File.

        Returns
        -------
        The existing or created group.

        See also
        --------
        create_group
        """
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
        """
        Open an existing dataset or create it if it does not exist.

        Parameters
        ----------
        name: str
            Name of the dataset. Must follow naming convention of parent Exdir File.
        shape: np.array, semi-optional
            Shape of the dataset. Must be set together with dtype.
            Cannot be set together with data, but must be set if data is not set.
            Will be used to verify that an existing dataset has the same shape or
            to create a new dataset of the given shape.
            See also `exact`.
        dtype: np.dtype, semi-optional
            NumPy datatype of the dataset. Must be set together with shape.
            Cannot be set together with data, but must be set if data is not set.
            Will be used to verify that an existing dataset has the same or a
            convertible dtype or to create a new dataset with the given dtype.
            See also `exact`.
        exact: bool, optional
            Only used if the dataset already exists.
            If `exact` is `False`, the shape must match the existing dataset and
            the data type must be convertible between the existing and requested
            data type.
            If `exact` is `True`, the `shape` and `dtype` must match exactly.
            The default is False.
            See also `shape`, `dtype` and `data`.
        data: list, np.array, semi-optional
            The data that will be used to create the dataset if it does not already exist.
            The shape and dtype of `data` will be compared to the existing dataset if it already exists.
            See `shape`, `dtype` and `exact`.
        fillvalue: scalar
            Used to create a dataset with the given `shape` and `type` with the
            initial value of `fillvalue`.
        """
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

        data, attrs, meta = ds._prepare_write(data, self.plugin_manager.dataset_plugins.write_order)

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
        """
        Checks the existence of an object with the given name in the group.

        Parameters
        ----------
        name: str
            the case-sensitive name of the object
        """
        if name == ".":
            return True
        if name == "":
            return False
        path = utils.path.name_to_asserted_group_path(name)
        directory = self.directory / path
        return exob.is_exdir_object(directory)

    def __getitem__(self, name):
        """
        Retrieves the object with the given name if it exists in the group.

        Parameters
        ----------
        name: str
            the case-sensitive name of the object to retrieve

        Raises
        ------
        KeyError:
            if the name does not correspond to an exdir object in the group
        """
        path = utils.path.name_to_asserted_group_path(name)
        if len(path.parts) > 1:
            top_directory = path.parts[0]
            sub_name = pathlib.PurePosixPath(*path.parts[1:])
            return self[top_directory][sub_name]

        if name not in self:
            error_message = "No such object: '{name}' in path '{path}'".format(
                name=name,
                path=str(self.directory)
            )
            raise KeyError(error_message)

        directory = self.directory / path

        if exob.is_raw_object_directory(directory):  # TODO create one function that handles all Raw creation
            return raw.Raw(
                root_directory=self.root_directory,
                parent_path=self.relative_path,
                object_name=name,
                io_mode=self.io_mode # TODO validate name?
                # TODO plugin manager?
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
            return self._dataset(name)
        elif meta_data[exob.EXDIR_METANAME][exob.TYPE_METANAME] == exob.GROUP_TYPENAME:
            return self._group(name)
        else:
            error_string = (
                "Object {name} has data type {type}.\n"
                "We cannot open objects of this type."
            ).format(
                name=name,
                type=meta_data[exob.EXDIR_METANAME][exob.TYPE_METANAME]
            )
            raise NotImplementedError(error_string)

    def _dataset(self, name):
        return ds.Dataset(
            root_directory=self.root_directory,
            parent_path=self.relative_path,
            object_name=name,
            io_mode=self.io_mode,
            name_validation=self.name_validation,
            plugin_manager=self.plugin_manager
        )

    def __setitem__(self, name, value):
        """
        Set or create a dataset with the given name from the given value.

        Parameters
        ----------
        name: str
            name of the existing or new dataset
        value: object
            value that will be used to create a new or set
            the contents of an existing dataset
        """
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
        """
        Returns
        -------
        KeysView
            A view of the names of the objects in the group.
        """
        return abc.KeysView(self)

    def items(self):
        """
        Returns
        -------
        ItemsView
            A view of the keys and objects in the group.
        """
        return abc.ItemsView(self)

    def values(self):
        """
        Returns
        -------
        ValuesView
            A view of the objects in the group.
        """
        return abc.ValuesView(self)

    def __iter__(self):
        """
        Iterate over all the objects in the group.
        """
        # NOTE os.walk is way faster than os.listdir + os.path.isdir
        directories = next(os.walk(str(self.directory)))[1]
        for name in sorted(directories):
            yield name
