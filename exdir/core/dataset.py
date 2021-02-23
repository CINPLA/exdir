import numbers
import numpy as np
import exdir

from . import exdir_object as exob
from .mode import assert_file_open, OpenMode, assert_file_writable

def _prepare_write(data, plugins, attrs, meta):
    for plugin in plugins:
        dataset_data = exdir.plugin_interface.DatasetData(
            data=data,
            attrs=attrs,
            meta=meta
        )
        dataset_data = plugin.prepare_write(dataset_data)

        data = dataset_data.data
        attrs = dataset_data.attrs
        meta = dataset_data.meta

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
    def __init__(self, root_directory, parent_path, object_name, file):
        super(Dataset, self).__init__(
            root_directory=root_directory,
            parent_path=parent_path,
            object_name=object_name,
            file=file
        )
        self._data_memmap = None
        self.plugin_manager = file.plugin_manager
        self.data_filename = str(_dataset_filename(self.directory))

    def __getitem__(self, args):
        assert_file_open(self.file)
        if len(self._data.shape) == 0:
            values = self._data
        else:
            values = self._data[args]

        enabled_plugins = [plugin_module.name for plugin_module in self.plugin_manager.plugins]

        data = values

        if "plugins" in self.meta:
            for plugin_name in self.meta["plugins"]:
                if ("required" in self.meta["plugins"][plugin_name]
                    and self.meta["plugins"][plugin_name]["required"] == True
                    and plugin_name not in enabled_plugins):
                    raise Exception((
                        "Plugin '{}' was used to write '{}', "
                        "but is not enabled."
                    ).format(plugin_name, self.name))

        plugins = self.plugin_manager.dataset_plugins.read_order

        if len(plugins) > 0:
            meta = self.meta.to_dict()
            atts = self.attrs.to_dict()

            dataset_data = exdir.plugin_interface.DatasetData(data=values,
                                                              attrs=self.attrs.to_dict(),
                                                              meta=meta)
            for plugin in plugins:
                dataset_data = plugin.prepare_read(dataset_data)

            data = dataset_data.data

        return data

    def __setitem__(self, args, value):
        assert_file_writable(self.file)

        value, attrs, meta = _prepare_write(
            data=value,
            plugins=self.plugin_manager.dataset_plugins.write_order,
            attrs=self.attrs.to_dict(),
            meta=self.meta.to_dict()
        )
        self._data[args] = value
        self.attrs = attrs
        self.meta._set_data(meta)

    def _reload_data(self):
        assert_file_open(self.file)
        for plugin in self.plugin_manager.dataset_plugins.write_order:
            plugin.before_load(self.data_filename)

        if self.file.io_mode == OpenMode.READ_ONLY:
            mmap_mode = "r"
        else:
            mmap_mode = "r+"

        try:
            self._data_memmap = np.load(self.data_filename, mmap_mode=mmap_mode, allow_pickle=False)
            self.file._open_datasets[self.name] = self
        except ValueError as e:
            # Could be that it is a Git LFS file. Let's see if that is the case and warn if so.
            with open(self.data_filename, "r", encoding="utf-8") as f:
                test_string = "version https://git-lfs.github.com/spec/v1"
                contents = f.read(len(test_string))
                if contents == test_string:
                    raise IOError("The file '{}' is a Git LFS placeholder. "
                        "Open the the Exdir File with the Git LFS plugin or run "
                        "`git lfs fetch` first. ".format(self.data_filename))
                else:
                    raise e

    def _reset_data(self, value, attrs, meta):
        assert_file_open(self.file)
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
            self.attrs = attrs

        if meta:
            self.meta._set_data(meta)

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
        assert_file_open(self.file)
        return self[:]

    @data.setter
    def data(self, value):
        assert_file_open(self.file)
        if self._data.shape != value.shape or self._data.dtype != value.dtype:
            value, attrs, meta = _prepare_write(
                data=value,
                plugins=self.plugin_manager.dataset_plugins.write_order,
                attrs=self.attrs.to_dict(),
                meta=self.meta.to_dict()
            )
            self._reset_data(value, attrs, meta)
            return

        self[:] = value

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
        return self.data

    @value.setter
    def value(self, value):
        self.data = value

    def __len__(self):
        """ The size of the first axis.  TypeError if scalar."""
        assert_file_open(self.file)
        if len(self.shape) == 0:
            raise TypeError("Attempt to take len() of scalar dataset")
        return self.shape[0]

    def __iter__(self):
        """Iterate over the first axis.  TypeError if scalar.
        WARNING: Modifications to the yielded data are *NOT* written to file.
        """
        assert_file_open(self.file)

        if len(self.shape) == 0:
            raise TypeError("Can't iterate over a scalar dataset")

        for i in range(self.shape[0]):
            yield self[i]

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return "<Closed Exdir Dataset>"
        return "<Exdir Dataset {} shape {} dtype {}>".format(
            self.name, self.shape, self.dtype)

    @property
    def _data(self):
        assert_file_open(self.file)
        if self._data_memmap is None:
            self._reload_data()
        return self._data_memmap
