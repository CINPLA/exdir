import numbers
import numpy as np

from . import exdir_object as exob

def _prepare_write(data, dataset_plugins):
    attrs = {}
    meta = {}
    for plugin in dataset_plugins:
        data, plugin_attrs, plugin_meta = plugin.prepare_write(data)
        attrs.update(plugin_attrs)
        if "required" in plugin_meta and plugin_meta["required"] == True:
            meta[plugin._plugin_module.name] = plugin_meta

    if isinstance(data, (numbers.Number, tuple, str)):
        data = np.asarray(data, order="C")

    return data, attrs, meta


def _dataset_filename(dataset_directory):
    return dataset_directory / "data.npy"


class Dataset(exob.Object):
    """
    Dataset class

    Warnings
    --------
        This class modifies the view and it is possible to overwrite
        an existing dataset, which is different from the behavior in h5py.
    """
    def __init__(self, root_directory, parent_path, object_name, io_mode=None,
                 name_validation=None, plugin_manager=None):
        super(Dataset, self).__init__(
            root_directory=root_directory,
            parent_path=parent_path,
            object_name=object_name,
            io_mode=io_mode,
            name_validation=name_validation,
            plugin_manager=plugin_manager
        )
        self._data_memmap = None

        self.data_filename = str(_dataset_filename(self.directory))

    def __getitem__(self, args):
        if len(self._data.shape) == 0:
            values = self._data
        else:
            values = self._data[args]

        enabled_plugins = [plugin_module.name for plugin_module in self.plugin_manager.plugins]
        if "plugins" in self.meta:
            for plugin_name in self.meta["plugins"].keys():
                if not plugin_name in enabled_plugins:
                    raise Exception((
                        "Plugin '{}' was used to write '{}', "
                        "but is not enabled."
                    ).format(plugin_name, self.name))

        for plugin in self.plugin_manager.dataset_plugins.read_order:
            values = plugin.prepare_read(values, self.attrs)


        return values

    def __setitem__(self, args, value):
        if self.io_mode == self.OpenMode.READ_ONLY:
            raise IOError('Cannot write data to file in read only ("r") mode')

        value, attrs, meta = _prepare_write(value, self.plugin_manager.dataset_plugins.write_order)
        self.attrs.update(attrs)
        self.meta["plugins"] = meta

        self._data[args] = value

    def _reload_data(self):
        if self.io_mode == self.OpenMode.READ_ONLY:
            mmap_mode = "r"
        else:
            mmap_mode = "r+"

        self._data_memmap = np.load(self.data_filename, mmap_mode=mmap_mode)

    def _reset_data(self, value, attrs, meta):
        self._data_memmap = np.lib.format.open_memmap(
            self.data_filename,
            mode="w+",
            dtype=value.dtype,
            shape=value.shape
        )

        if len(value.shape) == 0:
            # scalars need to be set with itemset
            self._data_memmap.itemset(value)
        else:
            # replace the contents with the value
            self._data_memmap[:] = value

        # update attributes and plugin metadata
        if attrs:
            self.attrs.update(attrs)

        if meta:
            self.meta["plugins"] = meta

        return

    def set_data(self, data):
        """
        Warning
        -------
        Deprecated convenience function.
        Use :code:`dataset.data = data` instead.
        """
        raise DeprecationWarning(
            "set_data is deprecated. Use `dataset.data = data` instead."
        )
        self.value = data

    @property
    def data(self):
        """
        Property that gives access the entire dataset.
        Equivalent to calling :code:`dataset[:]`.

        Returns
        -------
        numpy.memmap
            The entire dataset.
        """
        return self[:]

    @data.setter
    def data(self, value):
        self.value = value

    @property
    def shape(self):
        """
        The shape of the dataset.
        Equivalent to calling :code:`dataset[:].shape`.

        Returns
        -------
        tuple
            The shape of the dataset.
        """
        return self[:].shape

    @property
    def size(self):
        """
        The size of the dataset.
        Equivalent to calling :code:`dataset[:].size`.

        Returns
        -------
        np.int64
            The size of the dataset.
        """
        return self[:].size

    @property
    def dtype(self):
        """
        The NumPy data type of the dataset.
        Equivalent to calling :code:`dataset[:].dtype`.

        Returns
        -------
        numpy.dtype
            The NumPy data type of the dataset.
        """
        return self[:].dtype

    @property
    def value(self):
        """
        Convenience alias for the :code:`data` property.

        Warning
        -------
        This property is only provided as a convenience to make the API
        interoperable with h5py.
        We recommend to use :code:`data` instead of :code:`value`.
        """
        return self[:]

    @value.setter
    def value(self, value):
        # TODO this should be in data, since value is deprecated
        if self._data.shape != value.shape or self._data.dtype != value.dtype:
            value, attrs, meta = _prepare_write(value, self.plugin_manager.dataset_plugins.write_order)
            self._reset_data(value, attrs, meta)
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
