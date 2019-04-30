.. _plugins:

Plugins
=======

The functionality of Exdir can be extended with plugins.
These allow modifying the behavior of Exdir when enabled.
For instance, dataset and attribute plugins can perform pre- and post-processing of data during
reading and writing operations.
Note that plugins do not change the underlying specifications of Exdir.
Plugins are intended to perform verification of data consistency,
and to provide convenient mapping from general in-memory objects to objects that can be stored in
the Exdir format and back again.
Some plugins are provided in the exdir.plugins module,
while new plugins can be defined by Exdir users or package developers.

One of the built-in plugins provides experimental support for units using the `quantities` package:

.. code-block:: python

    >>> import exdir
    >>> import exdir.plugins.quantities
    >>> import quantities as pq
    >>> f = exdir.File("test.exdir", plugins=[exdir.plugins.quantities])
    >>> q = np.array([1,2,3])*pq.mV
    >>> dset_q = f.create_dataset("quantities_array", data=q)
    >>> dset_q[:]
    array([ 1.,  2.,  3.]) * mV

As shown in the above example, a plugin is enabled when creating a File object by passing the
plugin to the plugins argument.

To create a custom plugin, one of the handler classes in `exdir.plugin_interface` must be inherited.
The abstract handler classes are named after the object type you want to create a handler for.
In this example we have a simplified `Quantity` class,
which only contains a magnitude and a corresponding unit:

.. code-block:: python

    >>> class Quantity:
    >>>     def __init__(self, magnitude, unit):
    >>>         self.magnitude = magnitude
    >>>         self.unit = unit

Below, we create a plugin that enables us to directly use a `Quantity` object as a `Dataset` in
Exdir.
We do this by inheriting from `exdir.plugin_interface.Dataset` and overloading `prepare_write` and
`prepare_read`:

.. code-block:: python

    >>> import exdir
    >>> class DatasetQuantity(exdir.plugin_interface.Dataset):
    >>>     def prepare_write(self, dataset_data):
    >>>         magnitude = dataset_data.data.magnitude
    >>>         unit = dataset_data.data.unit
    >>>
    >>>         dataset_data.data = magnitude
    >>>         dataset_data.attrs = {"unit": unit}
    >>>
    >>>         return dataset_data
    >>>
    >>>     def prepare_read(self, dataset_data):
    >>>         unit = dataset_data.attrs["unit"]
    >>>         magnitude = dataset_data.data
    >>>
    >>>         dataset_data.data = Quantity(magnitude, unit)
    >>>
    >>>         return dataset_data

The overloaded functions take `dataset_data` as an argument.
This has the `data`, `attrs`, and `meta` properties.
The property `attrs` is a dictionary with optional attributes,
while `meta` is a dictionary with information about the plugin.

In `prepare_write`, the magnitude and unit of the data is translated to a value (numeric or
`numpy.ndarray`) and an attribute (dictionary-like) that then can be written to file.
`prepare_read` receives the data from the NumPy file and the attributes from the YAML file,
and uses these to reconstruct a `Quantity` object.

We create a plugin that uses this handler as follows:

.. code-block:: python

    >>> my_plugin = exdir.plugin_interface.Plugin(
    >>>    name="dataset_quantity",
    >>>    dataset_plugins=[DatasetQuantity()]
    >>> )

The plugin is enabled when opening a File by passing it to the plugins parameter:

.. code-block:: python

    >>> f = exdir.File("test.exdir", plugins=[my_plugin])
    >>> dset = f.create_dataset("test", data=Quantity(1.5, "meter"))

