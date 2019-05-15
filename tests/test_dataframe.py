# -*- coding: utf-8 -*-

# This file is part of Exdir, the Experimental Directory Structure.
#
# Copyright 2017 Simen Tennøe
#
# License: MIT, see "LICENSE" file for the full license terms.
#
# This file contains code from h5py, a Python interface to the HDF5 library,
# licensed under a standard 3-clause BSD license
# with copyright Andrew Collette and contributors.
# See http://www.h5py.org and the "3rdparty/h5py-LICENSE" file for details.


import pytest
import numpy as np
import pandas as pd
import os

from exdir.core import Attribute, File, Dataset

# TODO add the code below for testing true equality when parallelizing
# def __eq__(self, other):
# self[:]
# if isinstance(other, self.__class__):
#     other[:]
#     if self.__dict__.keys() != other.__dict__.keys():
#         return False
#
#     for key in self.__dict__:
#         if key == "_data":
#             if not np.array_equal(self.__dict__["_data"], other.__dict__["_data"]):
#                 return False
#         else:
#             if self.__dict__[key] != other.__dict__[key]:
#                 return False
#     return True
# else:
#     return False


# NOTE feather converts integer column names to str
def dataframe_equal(orig_df, new_df):
    columns = []
    for col1, col2 in zip(orig_df.columns, new_df.columns):
        try:
            columns.append(int(col2)==int(col1))
        except:
            columns.append(col2==col1)
    index = []
    for row1, row2 in zip(orig_df.index, new_df.index):
        try:
            index.append(int(row2)==int(row1))
        except:
            index.append(row2==row1)
    result = (
        np.array_equal(orig_df.values, new_df.values) and
        all(columns) and
        all(index)
    )
    return result


def test_create_empty(setup_teardown_file):
    """Create a scalar dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    data = pd.DataFrame([])
    dset = grp.create_dataset('foo', data=data)
    assert dset.shape == (0,0)
    assert dset.data.equals(data)


def test_create_scalar(setup_teardown_file):
    """Create a size-1 dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    data = pd.DataFrame([1])
    dset = grp.create_dataset('foo', data=data)
    assert dset.shape == (1,1)
    assert dset.shape == dset.data.shape
    assert dataframe_equal(data, dset.data)


def test_create_extended(setup_teardown_file):
    """Create an extended dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    data = pd.DataFrame(np.arange(63))
    dset = grp.create_dataset('foo', data=data)
    assert dset.shape == (63,1)
    assert dset.size == 63

    data = pd.DataFrame(np.zeros((6,10)))
    dset = f.create_dataset('bar', data=data)
    assert dset.shape == (6, 10)
    assert dset.size == (60)


def test_no_dtype(setup_teardown_file):
    """Confirm that datafram has no dtype."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = pd.DataFrame(np.zeros((6,10)))
    dset = f.create_dataset('bar', data=data)
    with pytest.raises(AttributeError):
        dset.dtype


def test_no_dtype_create(setup_teardown_file):
    """Confirm that one can force dtype """
    f = setup_teardown_file[3]
    data = pd.DataFrame(np.zeros((6,10)))
    with pytest.raises(NotImplementedError):
        f.create_dataset('bar', data=data, dtype=np.int16)


def test_numpy_then_dataframe(setup_teardown_file):
    """Confirm that datafram has no dtype."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = pd.DataFrame(np.zeros((6,10)))
    dset = f.create_dataset('bar', (6,10))
    assert isinstance(f['bar'].data, np.ndarray)
    f['bar'] = data
    assert np.array_equal(f['bar'].data.values, data.values)
    assert isinstance(f['bar'].data, pd.DataFrame)
    assert not (dset.directory / 'data.npy').exists()


def test_datafram_then_numpy(setup_teardown_file):
    """Confirm that datafram has no dtype."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = pd.DataFrame(np.zeros((6,10)))
    dset = f.create_dataset('bar', data=data)
    assert isinstance(f['bar'].data, pd.DataFrame)
    f['bar'] = np.zeros((6,10))
    assert np.array_equal(f['bar'].data, np.zeros((6,10)))
    assert isinstance(f['bar'].data, np.ndarray)
    assert not (dset.directory / 'data.feather').exists()


def test_reshape(setup_teardown_file):
    """Create from existing data, and make it fit a new shape."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = pd.DataFrame(np.zeros((6,10)))
    with pytest.raises(NotImplementedError):
        dset = grp.create_dataset('foo', shape=(10, 3), data=data)


# # Feature: Datasets can be created only if they don't exist in the file
def test_create(setup_teardown_file):
    """Create new dataset with no conflicts."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = pd.DataFrame(np.zeros((10, 3)))
    dset = grp.require_dataset('foo', (10, 3))
    assert isinstance(dset, Dataset)
    assert dset.shape == (10, 3)

    with pytest.raises(RuntimeError):
        grp.create_dataset('foo', (10, 3))


def test_create_existing_shape_mismatch(setup_teardown_file):
    """require_dataset yields existing dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data2 = pd.DataFrame(np.zeros((3, 10)))
    data3 = pd.DataFrame(np.zeros((4, 11)))
    dset2 = grp.require_dataset('bar', data=data2)
    dset3 = grp.require_dataset('bar', data=data3)
    assert isinstance(dset2, Dataset)
    assert dataframe_equal(dset2.data, data2)
    assert dataframe_equal(dset3.data, data2)
    assert dset2 == dset3


def test_create_existing_same_shape(setup_teardown_file):
    """require_dataset yields existing dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data2 = pd.DataFrame((3, 10))
    data3 = pd.DataFrame((4, 11))
    dset2 = grp.require_dataset('bar', data=data2)
    dset3 = grp.require_dataset('bar', data=data3)
    assert isinstance(dset2, Dataset)
    assert dataframe_equal(dset2.data, data2)
    assert dataframe_equal(dset3.data, data2)
    assert dset2 == dset3


def test_create_existing_df_to_npy(setup_teardown_file):
    """require_dataset yields existing dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data2 = pd.DataFrame((3, 10))
    data3 = np.zeros((1, 2))
    dset2 = grp.require_dataset('bar', data=data2)
    with pytest.raises(IOError):
        grp.require_dataset('bar', data=data3)


def test_create_existing_npy_to_df(setup_teardown_file):
    """require_dataset yields existing dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data2 = np.zeros((1, 2))
    data3 = pd.DataFrame((3, 10))
    dset2 = grp.require_dataset('bar', data=data2)
    with pytest.raises(IOError):
        grp.require_dataset('bar', data=data3)


def test_compound(setup_teardown_file):
    """Fill value works with compound types."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dt = np.dtype([('a', 'f4'), ('b', 'i8')])
    v = np.ones((1,), dtype=dt)
    data = pd.DataFrame(v)
    dset = grp.create_dataset('foo', data=data)
    assert dataframe_equal(dset.data, data)


def test_variable_length_string_numpy(setup_teardown_file):
    """Assignement of variable-length byte string produces a fixed-length
    ascii dataset """
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    # unable to change length of string with setitem
    data = np.array(['a', 'aa'])
    dset = grp.create_dataset('foo', data=data)
    dset[1] = 'aaaaaa'
    assert np.array_equal(dset.data, data)

# sjekk at setterne faktisk endrer på fil
def test_variable_length_string_df(setup_teardown_file):
    """Assignement of variable-length byte string produces a fixed-length
    ascii dataset """
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    # one needs object dtype in order to be able to change length of string with setitem
    values = ['a', 'aa']
    data = pd.DataFrame(values).T
    dset = grp.create_dataset('foo', data=data)

    dset['1'] = 'aaaaaa'
    values[1] = 'aaaaaa'
    assert np.array_equal(dset.data.values[0], values)
    dset._reload_data()
    assert np.array_equal(dset.data.values[0], values)


def test_flush(setup_teardown_file):
    """Assignement of variable-length byte string produces a fixed-length
    ascii dataset """
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    # one needs object dtype in order to be able to change length of string with setitem
    values = ['a', 'aa']
    data = pd.DataFrame(values).T
    dset = grp.create_dataset('foo', data=data)
    # using iloc changes data only in memory
    values[1] = 'aaaaaa'
    dset.data.iloc[0,1] = 'aaaaaa'
    assert np.array_equal(dset.data.values[0], values)
    dset._reload_data()
    assert dataframe_equal(dset.data, data)
    # flush saves data to file
    dset.data.iloc[0,1] = 'aaaaaa'
    dset.flush()
    dset._reload_data()
    assert np.array_equal(dset.data.values[0], values)


# Feature: Size of first axis is available via Python's len
def test_len(setup_teardown_file):
    """len()."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    data = pd.DataFrame(np.zeros((3, 10)))
    dset = grp.require_dataset('bar', data=data)
    assert len(dset) == 3

# Feature: Iterating over a dataset yields index keys

def test_iter(setup_teardown_file):
    """Iterating over a dataset yields rows."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    values = np.arange(30, dtype='f').reshape((10, 3))
    data = pd.DataFrame(values)
    dset = grp.create_dataset('foo', data=data)
    for x, y in zip(dset, data):
        assert x == str(y) # NOTE feather converts int names to str


def test_set_data(setup_teardown_file):
    """Set data works correctly."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    testdata = pd.DataFrame(np.ones((10, 2)))
    grp['testdata'] = testdata
    outdata = grp['testdata'].data
    assert dataframe_equal(testdata, outdata)

    grp['testdata'] = testdata
