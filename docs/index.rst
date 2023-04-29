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
   getting_started
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
With `PyPi <https://pypi.org/>`_::

    pip install exdir

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

Datasets are updated **on file** with:

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

Acknowledgements
----------------

The development of Exdir owes a great deal to other standardization efforts in science in general and neuroscience in particular,
among them the contributors to HDF5, NumPy, YAML, PyYAML, ruamel-yaml, SciPy, Klusta Kwik, NeuralEnsemble, and Neurodata Without Borders.

References
----------

* :ref:`genindex`
* :ref:`search`
