.. _quick:


Quick Start Guide
=================

Install
-------

With `Anaconda <http://continuum.io/downloads>`_ or
`Miniconda <http://conda.pydata.org/miniconda.html>`_::

    conda install -c cinpla exdir


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
