:orphan:

.. _getting_started:

Getting Started
===============

Quick usage example
-------------------

.. testsetup::

   import os
   import shutil
   if(os.path.exists("mytestfile.exdir")):
          shutil.rmtree("mytestfile.exdir")


.. doctest::

    >>> import exdir
    >>> import numpy as np
    >>> f = exdir.File("mytestfile.exdir")

The :ref:`File object <file>` points to the root folder in the exdir file
structure.
You can add groups and datasets to it.

.. doctest::

    >>> my_group = f.require_group("my_group")
    >>> a = np.arange(100)
    >>> dset = f.require_dataset("my_data", data=a)

These can later be accessed with square brackets:

.. doctest::

    >>> f["my_data"][10]
    10

Groups can hold other groups or datasets:

.. doctest::

    >>> subgroup = my_group.require_group("subgroup")
    >>> subdata = subgroup.require_dataset("subdata", data=a)

Datasets support array-style slicing:

.. doctest::

    >>> dset[0:100:10]
    memmap([ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90])

Datasets are updated with:

.. doctest::

    >>> dset[0:100:10] = a[0:100:10][::-1]
    >>> dset[0:100:10]
    memmap([90, 80, 70, 60, 50, 40, 30, 20, 10,  0])

Attributes can be added to files, groups and datasets:

.. doctest::

    >>> f.attrs["description"] = "My first exdir file"
    >>> my_group.attrs["meaning_of_life"] = 42
    >>> dset.attrs["trial_number"] = 12
    >>> f.attrs["description"]
    'My first exdir file'

Core concepts
-------------
An exdir object contains two types of objects: `datasets`, which are
array-like collections of data, and `groups`, which are directories containing
datasets and other groups.

An exdir directory is created by:

.. testsetup::

   import os
   import shutil
   if(os.path.exists("myfile.exdir")):
          shutil.rmtree("myfile.exdir")


.. doctest::

    >>> import exdir
    >>> import numpy as np
    >>> f = exdir.File("myfile.exdir", "w")

The :ref:`File object <file>` containes many useful methods including :py:meth:`exdir.core.Group.require_dataset`:

    >>> data = np.arange(100)
    >>> dset = f.require_dataset("mydataset", data=data)

The created object is not an array but :ref:`an exdir dataset<dataset>`.
Like NumPy arrays, datasets have a shape:

    >>> dset.shape
    (100,)

Also array-style slicing is supported:

    >>> dset[0]
    0
    >>> dset[10]
    10
    >>> dset[0:100:10]
    memmap([ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90])

Datasets are updated **on file**:

.. doctest::

    >>> dset[0:100:10] = a[0:100:10][::-1]
    >>> dset[0:100:10]
    memmap([90, 80, 70, 60, 50, 40, 30, 20, 10,  0])
    >>> dset.data = np.arange(10)
    >>> dset
    memmap([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

For more, see :ref:`file` and :ref:`dataset`.

A Group is a container of other groups, datasets and raw objects.

To create a Group it is necessary to have a File object available::

    >>> f = exdir.File('my_file')
    >>> group = f.create_group('my_group')

Groups can contain other groups, datasets and raw objects::

    >>> group.create_group('other_group')
    >>> group.create_dataset('my_dataset', data=[0,1,2])
    >>> group.create_raw('raw_container')

Children of groups can be accessed by indexing::

    >>> group['my_dataset']
    memmap([ 0, 1, 2])

One may iterate groups similar to maps::

    >>> for key, value in group.items():
            print(group[key] == value)
    True
    True
    True
    >>> for key in group:
            print(key)

Attributes
----------

With exdir you can store metadata right next to the data it describes.
All groups and datasets can have attributes which are descibed by :py:meth:`exdir.core.attributes`.

Attributes are accessed through the ``attrs`` proxy object, which again
implements the dictionary interface:

    >>> dset.attrs['temperature'] = 99.5
    >>> dset.attrs['temperature']
    99.5
    >>> 'temperature' in dset.attrs
    True

Groups and Files may also have attributes::

    >>> group.attr = {'description': 'this is a group'}
    >>> group.attr['number'] = 1
    >>> print(group.attr)
    {'description': 'this is a group', 'number': 1}
    >>> f.attr = {'description': 'this is a file'}
    >>> f.attr['number'] = 2
    >>> print(f.attr)
    {'description': 'this is a file', 'number': 2}

For more, see :ref:`attributes`.

Groups and hierarchical organization
------------------------------------

Every object in an exdir directory has a name, and they're arranged in a POSIX-style hierarchy with ``/``-separators:

    >>> dset.name
    '/mydataset'

The "directory" in this system are called :ref:`groups <group>`.
The :ref:`File object <file>` we created is itself a group, in this case the `root group`, named ``/``

    >>> f.name
    '/'

Creating a subgroup is done by using :py:meth:`exdir.core.Group.require_group` method:

    >>> grp = f.require_group("subgroup")

All :py:class:`exdir.core.Group` objects also have the ``require_*`` methods like File:

    >>> dset2 = grp.require_dataset("another_dataset", data=data)
    >>> dset2.name
    '/subgroup/another_dataset'

.. By the way, you don't have to create all the intermediate groups manually.
.. Specifying a full path works just fine:
..
..
..     >>> dset3 = f.create_dataset('subgroup2/dataset_three', (10,))
..     >>> dset3.name
..     '/subgroup2/dataset_three'

You retrieve objects in the file using the item-retrieval syntax:

    >>> dataset_three = f['subgroup/another_dataset']

Iterating over a group provides the names of its members:

    >>> for name in f:
    ...     print(name)
    mydataset
    subgroup


Containership testing also uses names:


    >>> "mydataset" in f
    True
    >>> "somethingelse" in f
    False

You can even use full path names:

    >>> "subgroup/another_dataset" in f
    True
    >>> "subgroup/somethingelse" in f
    False

There are also the familiar :py:meth:`exdir.core.Group.keys`, :py:meth:`exdir.core.Group.values`, :py:meth:`exdir.core.Group.items` and
:py:meth:`exdir.core.Group.iter` methods, as well as :py:meth:`exdir.core.Group.get`.

For more, see :ref:`group`.

Raw
---

With exdir you can store raw data, that is any datatype you want to, in a `Raw` object.
The typical usecase is raw data produced in a format that you want to keep
alongside with data which is converted or processed
and stored in exdir datasets.

You can create `Raw` objects with:

.. doctest::

    >>> raw = f.create_raw('raw_filename')

Note that you may also use `require_raw`.
The `Raw` directory is available thorough:

.. doctest::

    >>> directory = raw.directory

For more, see :ref:`raw`.

Acknowledgements
----------------

The development of Exdir owes a great deal to other standardization efforts in science in general and neuroscience in particular,
among them the contributors to HDF5, NumPy, YAML, PyYAML, ruamel-yaml, SciPy, Klusta Kwik, NeuralEnsemble, and Neurodata Without Borders.

References
----------

* :ref:`genindex`
* :ref:`search`
