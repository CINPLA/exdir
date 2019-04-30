.. exdir documentation master file, created by
   sphinx-quickstart on Fri Feb  3 09:52:17 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Exdir's documentation!
=================================

The Experimental Directory Structure (Exdir) is a proposed, open file format specification for experimental pipelines.
Exdir uses the same abstractions as HDF5 and is compatible with the HDF5 Abstract Data Model, but stores data and metadata in directories instead of in a single file.
Exdir uses file system directories to represent the hierarchy, with metadata stored in human-readable YAML files, datasets stored in binary NumPy files, and raw data stored directly in subdirectories.
Furthermore, storing data in multiple files makes it easier to track for version control systems.
Exdir is not a file format in itself, but a specification for organizing files in a directory structure.
With the publication of Exdir, we invite the scientific community to join the development to create an open specification that will serve as many needs as possible and as a foundation for open access to and exchange of data.

Exdir is described in detail in our reasearch paper:

`Experimental Directory Structure (Exdir): An Alternative to HDF5 Without Introducing a New File Format <https://www.frontiersin.org/articles/10.3389/fninf.2018.00016/full>`_.

.. toctree::
   :maxdepth: 1
   :hidden:

   installation
   file
   group
   dataset
   raw
   attributes
   plugins

Specification
-------------

exdir is not a file format in itself, but rather a specification for a directory structure
with NumPy and YAML files.

.. code-block:: text

  example.exdir (File, folder)
  │   attributes.yaml (-, file)
  │   exdir.yaml (-, file)
  │
  ├── dataset1 (Dataset, folder)
  │   ├── data.npy (-, file)
  │   ├── attributes.yaml (-, file)
  │   └── exdir.yaml (-, file)
  │
  └── group1 (Group, folder)
      ├── attributes.yaml (-, file)
      ├── exdir.yaml (-, file)
      │
      └── dataset2 (Dataset, folder)
          ├── data.npy (-, file)
          ├── attributes.yaml (-, file)
          ├── exdir.yaml (-, file)
          │
          └── raw (Raw, folder)
              ├── image0001.tif (-, file)
              ├── image0002.tif (-, file)
              └── ...

The above structure shows the name of the object, the type of the object in exdir and
the type of the object on the file system as follows:

```
[name] ([exdir type], [file system type])
```

A dash (-) indicates that the object doesn't have a separate internal
representation in the format, but is used indirectly.
It is however explicitly stored in the file system.


Install
-------

With `Anaconda <http://continuum.io/downloads>`_ or
`Miniconda <http://conda.pydata.org/miniconda.html>`_::

    conda install -c cinpla exdir

For more, see :ref:`installation`.

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

For more, see :ref:`file` and :ref:`dataset`.


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


.. Since iterating over a group only yields its directly-attached members,
.. iterating over an entire file is accomplished with the ``Group`` methods
.. ``visit()`` and ``visititems()``, which take a callable:
..
..
..
..     >>> def printname(name):
..     ...     print(name)
..     >>> f.visit(printname)
..     mydataset
..     subgroup
..     subgroup/another_dataset
..     subgroup2
..     subgroup2/dataset_three

For more, see :ref:`group`.



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

For more, see :ref:`attributes`.

Acknowledgements
----------------

The development of Exdir owes a great deal to other standardization efforts in science in general and neuroscience in particular,
among them the contributors to HDF5, NumPy, YAML, PyYAML, ruamel-yaml, SciPy, Klusta Kwik, NeuralEnsemble, and Neurodata Without Borders.

References
----------

* :ref:`genindex`
* :ref:`search`
