import os
import numpy as np
import exdir

import quantities as pq

from . import exdir_object as exob

def _prepare_write(data):
    attrs = {}
    for plugin in exdir.dataset_plugins:
        data, plugin_attrs = plugin.prepare_write(data)
        attrs.update(plugin_attrs)

    if data is None:
        return None, attrs

    if not isinstance(data, np.ndarray):
        return np.asarray(data, order="C"), attrs

    return data, attrs

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

def _dataset_filename(dataset_directory):
    return dataset_directory / "data.npy"

# def _create_dataset_directory(dataset_directory, data):
#     exob._create_object_directory(dataset_directory, exob.DATASET_TYPENAME)
#     filename = str(_dataset_filename(dataset_directory))
#     np.save(filename, data)
#     # dataset = exob.open_object(filename)
#     # dataset._reset_data(data)
#
# def _extract_quantity(data):
#     attrs = {}
#     if isinstance(data, pq.Quantity):
#         result = data.magnitude
#         attrs["unit"] = data.dimensionality.string
#         if isinstance(data, pq.UncertainQuantity):
#             attrs["uncertainty"] = data.uncertainty
#     else:
#         result = data
#     return attrs, result
#
# def _convert_data(data, shape, dtype, fillvalue):
#     attrs = {}
#     if data is not None:
#         attrs, result = _extract_quantity(data)
#         if not isinstance(result, np.ndarray):
#             result = np.asarray(data, order="C", dtype=dtype)
#
#         if shape is not None and result.shape != shape:
#             result = np.reshape(result, shape)
#     else:
#         if shape is None:
#             result = None
#         else:
#             fillvalue = fillvalue or 0.0
#             result = np.full(shape, fillvalue, dtype=dtype)
#
#     if result is None:
#         raise TypeError("Could not create a meaningful dataset.")
#
#     return attrs, result

class Dataset(exob.Object):
    """
    Dataset class

    Warning: This class modifies the view, which is different from h5py.
    Warning: Possible to overwrite existing dataset.
             This differs from the h5py API. However,
             it should only cause issues with existing
             code if said code expects this to fail."
    """
    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 validate_name=None):
        super(Dataset, self).__init__(
            root_directory=root_directory,
            parent_path=parent_path,
            object_name=object_name,
            io_mode=io_mode,
            validate_name=validate_name
        )
        self._data_memmap = None
        if self.io_mode == self.OpenMode.READ_ONLY:
            self._mmap_mode = "r"
        else:
            self._mmap_mode = "r+"

        self.data_filename = str(_dataset_filename(self.directory))

    def __getitem__(self, args):
        if len(self._data.shape) == 0:
            values = self._data
        else:
            values = self._data[args]

        for plugin in exdir.dataset_plugins:
            values = plugin.prepare_read(values, self.attrs)

        return values

    def __setitem__(self, args, value):
        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError('Cannot write data to file in read only ("r") mode')

        value, attrs = _prepare_write(value)
        self.attrs.update(attrs)

        self._data[args] = value

    def _reload_data(self):
        self._data_memmap = np.load(self.data_filename, mmap_mode=self._mmap_mode)

    def _reset_data(self, value, skip_plugins=False):
        value, attrs = _prepare_write(value)

        np.save(self.data_filename, value)

        self.attrs.update(attrs)
        self._reload_data()
        return

    def set_data(self, data):
        raise DeprecationWarning(
            "set_data is deprecated. Use `dataset.value = data` instead."
        )
        self.value = data

    @property
    def data(self):
        return self[:]

    @data.setter
    def data(self, value):
        self.value = value

    @property
    def shape(self):
        return self[:].shape

    @property
    def size(self):
        return self[:].size

    @property
    def dtype(self):
        return self[:].dtype

    @property
    def value(self):
        return self[:]

    @value.setter
    def value(self, value):
        if self._data.shape != value.shape:
            self._reset_data(value)
            return

        self[:] = value

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

    @property
    def _data(self):
        if self._data_memmap is None:
            self._reload_data()
        return self._data_memmap
