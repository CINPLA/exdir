:orphan:

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
An exdir file is a container for two kinds of objects: `datasets`, which are
array-like collections of data, and `groups`, which are directory-like containers
that hold datasets and other groups. The most fundamental thing to remember
when using exdir is:

    **Groups work like dictionaries, and datasets work like NumPy arrays**

The very first thing you'll need to do is create a new file::

    >>> import exdir
    >>> import numpy as np
    >>>
    >>> f = exdir.File("mytestfile.exdir")

The :ref:`File object <file>` is your starting point.  It has a couple of
methods which look interesting.  One of them is ``require_dataset``::

    >>> a = np.arange(100)
    >>> dset = f.require_dataset("mydata", data=a)

The object we created isn't an array, but ().
Like NumPy arrays, datasets have both a shape and a data type:

    >>> dset.shape
    (100,)

They also support array-style slicing.  This is how you read and write data
from a dataset in the file:

    >>> dset[0]
    1
    >>> dset[10]
    10
    >>> dset[0:100:10]
    array([ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90])

For more, see :ref:`file` and :ref:`dataset`.
