.. exdir documentation master file, created by
   sphinx-quickstart on Fri Feb  3 09:52:17 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to exdir's documentation!
=================================

The Experimental Directory Structure (exdir) is a proposed, open file format standard for
experimental pipelines.
exdir is currently a prototype published to invite researchers to give feedback on
the standard.

exdir is an hierarchical format based on open standards.
It is inspired by already existing formats, such as HDF5 and NumPy,
and attempts to solve some of the problems assosciated with these while
retaining their benefits.
The development of exdir owes a great deal to the efforts of others to standardize
data formats in science in general and neuroscience in particular, among them 
the Klusta Kwik Team and Neuroscience Without Borders.

.. toctree::
   :maxdepth: 1
   :hidden:
   
   quick
   installation
   file
   group
   dataset
   attributes
   file_format

File format
-----------

exdir is not a file format in itself, but rather a standardized folder structure.

.. code-block:: text

  example.exdir (File, folder)
  │   attributes.yml (-, file)
  │   meta.yml (-, file)
  │
  ├── dataset1 (Dataset, folder)
  │   ├── data.npy (-, file)
  │   ├── attributes.yml (-, file)
  │   └── meta.yml (-, file)
  │
  └── group1 (Group, folder)
      ├── attributes.yml (-, file)
      ├── meta.yml (-, file)
      │
      └── dataset2 (Dataset, folder)
          ├── data.npy (-, file)
          ├── attributes.yml (-, file)
          ├── meta.yml (-, file)
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

Usage
-----

    >>> import exdir
    >>> import numpy as np
    >>> f = exdir.File("mytestfile.exdir")

The :ref:`File object <file>` points to the root folder in the exdir file
structure.
You can add groups and datasets to it.

    >>> my_group = f.require_group("my_group")
    >>> a = np.arange(100)
    >>> dset = f.require_dataset("my_data", data=a)

These can later be accessed with square brackets:

    >>> f["my_data"][10]
    10

Groups can hold other groups or datasets:

    >>> subgroup = my_group.require_group("subgroup")
    >>> subgroup.require_dataset("subdata", data=a)
    
Datasets support array-style slicing:

    >>> dset[0:100:10]
    array([ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
    
Attributes can be added to files, groups and datasets:

    >>> f.attrs["description"] = "My first exdir file"
    >>> my_group.attrs["meaning_of_life"] = 42
    >>> dset.attrs["trial_number"] = 12
    >>> f.attrs["description"]
    'My first exdir file'

References
----------

* :ref:`genindex`
* :ref:`search`
