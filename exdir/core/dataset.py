import os
import quantities as pq
import numpy as np

from . import quantities_conversion as pqc

from . import exdir_object


class Dataset(exdir_object.Object):
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
        super(Dataset, self).__init__(root_directory=root_directory,
                                      parent_path=parent_path,
                                      object_name=object_name,
                                      io_mode=io_mode,
                                      validate_name=validate_name)
        self.data_filename = self.directory / "data.npy"
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
            # NOTE using str(filename) because of Python 3.5 and NumPy 1.11 support
            np.save(str(self.data_filename), result)

            # TODO should we have this line?
            #      Might lead to bugs where we create data, but havent loaded it
            #      but requires the data always stay in memory
            # self._data = result


    def __getitem__(self, args):
        if not self.data_filename.exists():
            return np.array([])

        if self._data is None:
            # NOTE using str(filename) because of Python 3.5 and NumPy 1.11 support
            self._data = np.load(str(self.data_filename), mmap_mode=self._mmap_mode)

        if len(self._data.shape) == 0:
            values = self._data
        else:
            values = self._data[args]

        if "unit" in self.attrs:
            item_dict = {"value": values,
                         "unit": self.attrs["unit"]}
            if "uncertainty" in self.attrs:
                item_dict["uncertainty"] = self.attrs["uncertainty"]

            values = pqc.convert_back_quantities(item_dict)

        return values

    def __setitem__(self, args, value):
        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError('Cannot write data to file in read only ("r") mode')
        if self._data is None:
            self[:]  # TODO what is this good for?
        self._data[args] = value

    @property
    def data(self):
        return self[:]

    @data.setter
    def data(self, value):
        self.set_data(data=value)

    @property
    def shape(self):
        return self[:].shape

    @property
    def size(self):
        return self[:].size

    @property
    def dtype(self):
        return self[:].dtype

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
