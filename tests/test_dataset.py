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


# Feature: Datasets can be created from a shape only

def test_create_scalar(setup_teardown_file):
    """Create a scalar dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', ())
    assert dset.shape == ()
    assert dset.data == 0

def test_create_simple(setup_teardown_file):
    """Create a size-1 dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (1,))
    assert dset.shape == (1,)

def test_create_extended(setup_teardown_file):
    """Create an extended dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (63,))
    assert dset.shape == (63,)
    assert dset.size == 63

    dset = f.create_dataset('bar', (6, 10))
    assert dset.shape == (6, 10)
    assert dset.size == (60)

def test_default_dtype(setup_teardown_file):
    """Confirm that the default dtype is float."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (63,))
    assert dset.dtype == np.dtype('float32')

def test_missing_shape(setup_teardown_file):
    """Missing shape raises TypeError."""
    f = setup_teardown_file[3]

    with pytest.raises(TypeError):
        f.create_dataset('foo')

def test_long_double(setup_teardown_file):
    """Confirm that the default dtype is float """
    f = setup_teardown_file[3]

    dset = f.create_dataset('foo', (63,), dtype=np.int16)
    assert dset.dtype == np.int16


 # Feature: Datasets can be created from existing data
def test_create_scalar_data(setup_teardown_file):
    """Create a scalar dataset from existing array."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = np.ones((), 'f')
    dset = grp.create_dataset('foo', data=data)
    assert dset.shape == data.shape


def test_create_extended_data(setup_teardown_file):
    """Create an extended dataset from existing data."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = np.ones((63,), 'f')
    dset = grp.create_dataset('foo', data=data)
    assert dset.shape == data.shape

def test_dataset_intermediate_group(setup_teardown_file):
    """Create dataset with missing intermediate groups."""
    f = setup_teardown_file[3]

    # Trying to create intermediate groups that are absolute should fail just
    # like when creating them on groups.
    with pytest.raises(NotImplementedError):
        f.create_dataset("/foo/bar/baz", shape=(10, 10), dtype='<i4')

    ds = f.create_dataset("foo/bar/baz", shape=(10, 10), dtype='<i4')
    assert isinstance(ds, Dataset)
    assert "/foo/bar/baz" in f

def test_reshape(setup_teardown_file):
    """Create from existing data, and make it fit a new shape."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = np.arange(30, dtype='f')
    dset = grp.create_dataset('foo', shape=(10, 3), data=data)
    assert dset.shape == (10, 3)
    assert np.array_equal(dset.data, data.reshape((10, 3)))

# Feature: Datasets can be created only if they don't exist in the file
def test_create(setup_teardown_file):
    """Create new dataset with no conflicts."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.require_dataset('foo', (10, 3), 'f')
    assert isinstance(dset, Dataset)
    assert dset.shape == (10, 3)

    dset2 = grp.require_dataset('bar', data=(3, 10))
    dset3 = grp.require_dataset('bar', data=(4, 11))
    assert isinstance(dset2, Dataset)
    assert np.all(dset2[:] == (3, 10))
    assert np.all(dset3[:] == (3, 10))
    assert dset2 == dset3

def test_create_existing(setup_teardown_file):
    """require_dataset yields existing dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")


    dset = grp.require_dataset('foo', (10, 3), 'float32')
    dset2 = grp.require_dataset('foo', (10, 3), 'float32')

    assert dset == dset2


def test_shape_conflict(setup_teardown_file):
    """require_dataset with shape conflict yields TypeError."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp.create_dataset('foo', (10, 3), 'f')
    with pytest.raises(TypeError):
        grp.require_dataset('foo', (10, 4), 'f')


def test_type_confict(setup_teardown_file):
    """require_dataset with object type conflict yields TypeError."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp.create_group('foo')
    with pytest.raises(TypeError):
        grp.require_dataset('foo', (10, 3), 'f')


def test_dtype_conflict(setup_teardown_file):
    """require_dataset with dtype conflict (strict mode) yields TypeError."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (10, 3), 'f')
    with pytest.raises(TypeError):
        grp.require_dataset('foo', (10, 3), 'S10')


def test_dtype_close(setup_teardown_file):
    """require_dataset with convertible type succeeds (non-strict mode)-"""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (10, 3), 'i4')
    dset2 = grp.require_dataset('foo', (10, 3), 'i2', exact=False)
    assert dset == dset2
    assert dset2.dtype == np.dtype('i4')


# Feature: Datasets can be created with fill value

def test_create_fillval(setup_teardown_file):
    """Fill value is reflected in dataset contents."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (10,), fillvalue=4.0)
    assert dset[0] == 4.0
    assert dset[7] == 4.0



def test_compound(setup_teardown_file):
    """Fill value works with compound types."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dt = np.dtype([('a', 'f4'), ('b', 'i8')])
    v = np.ones((1,), dtype=dt)[0]
    dset = grp.create_dataset('foo', (10,), dtype=dt, fillvalue=v)


def test_exc(setup_teardown_file):
    """Bogus fill value raises TypeError."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    with pytest.raises(TypeError):
        grp.create_dataset('foo', (10,), dtype="float32", fillvalue={"a": 2})


def test_string(setup_teardown_file):
    """Assignement of fixed-length byte string produces a fixed-length
    ascii dataset """
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', data="string")
    assert dset.data == "string"



# Feature: Dataset dtype is available as .dtype property

def test_dtype(setup_teardown_file):
    """Retrieve dtype from dataset."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (5,), '|S10')
    assert dset.dtype == np.dtype('|S10')


# Feature: Size of first axis is available via Python's len
def test_len(setup_teardown_file):
    """len()."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (312, 15))
    assert len(dset) == 312


def test_len_scalar(setup_teardown_file):
    """len()  of scalar)."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset =grp.create_dataset('foo', data=1)
    with pytest.raises(TypeError):
        len(dset)


# Feature: Iterating over a dataset yields rows

def test_iter(setup_teardown_file):
    """Iterating over a dataset yields rows."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    data = np.arange(30, dtype='f').reshape((10, 3))
    dset = grp.create_dataset('foo', data=data)
    for x, y in zip(dset, data):
        assert len(x) == 3
        assert np.array_equal(x, y)


def test_iter_scalar(setup_teardown_file):
    """Iterating over scalar dataset raises TypeError."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', shape=())
    with pytest.raises(TypeError):
        [x for x in dset]


def test_trailing_slash(setup_teardown_file):
    """Trailing slashes are unconditionally ignored."""
    f = setup_teardown_file[3]

    f["dataset"] = 42
    assert "dataset/" in  f


# Feature: Compound types correctly round-trip
def test_compund(setup_teardown_file):
    """Compound types are read back in correct order."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dt = np.dtype( [('weight', np.float64),
                    ('cputime', np.float64),
                    ('walltime', np.float64),
                    ('parents_offset', np.uint32),
                    ('n_parents', np.uint32),
                    ('status', np.uint8),
                    ('endpoint_type', np.uint8)])

    testdata = np.ndarray((16,), dtype=dt)
    for key in dt.fields:
        testdata[key] = np.random.random((16,))*100

    # print(testdata)

    grp['test'] = testdata
    outdata = grp['test'][()]
    assert np.all(outdata == testdata)
    assert outdata.dtype == testdata.dtype

def test_assign(setup_teardown_file):
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dt = np.dtype([('weight', (np.float64, 3)),
                   ('endpoint_type', np.uint8),])

    testdata = np.ndarray((16,), dtype=dt)
    for key in dt.fields:
        testdata[key] = np.random.random(size=testdata[key].shape)*100

    ds = grp.create_dataset('test', (16,), dtype=dt)
    for key in dt.fields:
        ds[key] = testdata[key]

    outdata = f['test']["test"][()]

    assert np.all(outdata == testdata)
    assert outdata.dtype == testdata.dtype




def test_set_data(setup_teardown_file):
    """Set data works correctly."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    testdata = np.ones((10, 2))
    grp['testdata'] = testdata
    outdata = grp['testdata'][()]
    assert np.all(outdata == testdata)
    assert outdata.dtype == testdata.dtype

    grp['testdata'] = testdata




def test_eq_false(setup_teardown_file):
    """__eq__."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', data=1)
    dset2 = grp.create_dataset('foobar', (2, 2))

    assert dset != dset2
    assert not dset == 2

def test_eq(setup_teardown_file):
    """__eq__."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', data=np.ones((2, 2)))

    assert dset == dset


def test_mmap(setup_teardown_file):
    """Test that changes to a mmap loaded numpy file is written to disk"""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('foo', (10**3, 10**3), fillvalue=2)
    dset[1, 1] = 100

    tmp_file = np.load(str(setup_teardown_file[1] / "test" / "foo" / "data.npy"))

    assert dset.data[1, 1] == 100
    assert tmp_file[1, 1] == 100


def test_modify_view(setup_teardown_file):
    f = setup_teardown_file[3]
    dataset = f.create_dataset("mydata", data=np.array([1, 2, 3, 4, 5, 6, 7, 8]))
    dataset[3:5] = np.array([8, 9])
    assert np.array_equal(f["mydata"][3:5], np.array([8, 9]))
    view = dataset[3:5]
    view[0] = 10
    assert f["mydata"][3] == 10


def test_single_index(setup_teardown_file):
    """Single-element selection with [index] yields array scalar."""
    f = setup_teardown_file[3]
    dset = f.create_dataset('x', (1,), dtype='i1')
    out = dset[0]
    assert isinstance(out, np.int8)

def test_single_null(setup_teardown_file):
    """Single-element selection with [()] yields ndarray."""
    f = setup_teardown_file[3]

    dset = f.create_dataset('x', (1,), dtype='i1')
    out = dset[()]
    assert isinstance(out, np.ndarray)
    assert out.shape == (1,)

def test_scalar_index(setup_teardown_file):
    """Slicing with [...] yields scalar ndarray."""
    f = setup_teardown_file[3]

    dset = f.create_dataset('x', shape=(), dtype='f')
    out = dset[...]
    assert isinstance(out, np.ndarray)
    assert out.shape == ()

def test_scalar_null(setup_teardown_file):
    """Slicing with [()] yields array scalar."""
    f = setup_teardown_file[3]

    dset = f.create_dataset('x', shape=(), dtype='i1')
    out = dset[()]

    assert out.dtype == "int8"

def test_compound_index(setup_teardown_file):
    """Compound scalar is numpy.void, not tuple."""
    f = setup_teardown_file[3]

    dt = np.dtype([('a', 'i4'), ('b', 'f8')])
    v = np.ones((4,), dtype=dt)
    dset = f.create_dataset('foo', (4,), data=v)
    assert dset[0] == v[0]
    assert isinstance(dset[0], np.void)


# Feature: Simple NumPy-style slices (start:stop:step) are supported.

def test_negative_stop(setup_teardown_file):
    """Negative stop indexes work as they do in NumPy."""
    f = setup_teardown_file[3]

    arr = np.arange(10)
    dset = f.create_dataset('x', data=arr)

    assert np.array_equal(dset[2:-2], arr[2:-2])


# Feature: Array types are handled appropriately

def test_read(setup_teardown_file):
    """Read arrays tack array dimensions onto end of shape tuple."""
    f = setup_teardown_file[3]

    dt = np.dtype('(3,)f8')
    dset = f.create_dataset('x', (10,), dtype=dt)
    # TODO implement this
    # assert dset.shape == (10,)
    # assert dset.dtype == dt

    # Full read
    out = dset[...]
    assert out.dtype == np.dtype('f8')
    assert out.shape == (10, 3)

    # Single element
    out = dset[0]
    assert out.dtype == np.dtype('f8')
    assert out.shape == (3,)

    # Range
    out = dset[2:8:2]
    assert out.dtype == np.dtype('f8')
    assert out.shape == (3, 3)

def test_write_broadcast(setup_teardown_file):
    """Array fill from constant is  supported."""
    f = setup_teardown_file[3]

    dt = np.dtype('(3,)i')

    dset = f.create_dataset('x', (10,), dtype=dt)
    dset[...] = 42



def test_write_element(setup_teardown_file):
    """Write a single element to the array."""
    f = setup_teardown_file[3]

    dt = np.dtype('(3,)f8')
    dset = f.create_dataset('x', (10,), dtype=dt)

    data = np.array([1, 2, 3.0])
    dset[4] = data

    out = dset[4]
    assert np.all(out == data)


def test_write_slices(setup_teardown_file):
    """Write slices to array type."""
    f = setup_teardown_file[3]

    dt = np.dtype('(3,)i')

    data1 = np.ones((2, ), dtype=dt)
    data2 = np.ones((4, 5), dtype=dt)

    dset = f.create_dataset('x', (10, 9, 11), dtype=dt)

    dset[0, 0, 2:4] = data1
    assert np.array_equal(dset[0, 0, 2:4], data1)

    dset[3, 1:5, 6:11] = data2
    assert np.array_equal(dset[3, 1:5, 6:11], data2)


def test_roundtrip(setup_teardown_file):
    """Read the contents of an array and write them back."""
    f = setup_teardown_file[3]
    dt = np.dtype('(3,)f8')
    dset = f.create_dataset('x', (10,), dtype=dt)

    out = dset[...]
    dset[...] = out

    assert np.all(dset[...] == out)



# Feature Slices resulting in empty arrays


def test_slice_zero_length_dimension(setup_teardown_file):
    """Slice a dataset with a zero in its shape vector
       along the zero-length dimension."""
    f = setup_teardown_file[3]

    for i, shape in enumerate([(0,), (0, 3), (0, 2, 1)]):
        dset = f.create_dataset('x%d'%i, shape, dtype=np.int32)
        assert dset.shape == shape
        out = dset[...]
        assert isinstance(out, np.ndarray)
        assert out.shape == shape
        out = dset[:]
        assert isinstance(out, np.ndarray)
        assert out.shape == shape
        if len(shape) > 1:
            out = dset[:, :1]
            assert isinstance(out, np.ndarray)
            assert out.shape[:2] == (0, 1)

def test_slice_other_dimension(setup_teardown_file):
    """Slice a dataset with a zero in its shape vector
       along a non-zero-length dimension."""
    f = setup_teardown_file[3]

    for i, shape in enumerate([(3, 0), (1, 2, 0), (2, 0, 1)]):
        dset = f.create_dataset('x%d'%i, shape, dtype=np.int32)
        assert dset.shape == shape
        out = dset[:1]
        assert isinstance(out, np.ndarray)
        assert out.shape == (1,)+shape[1:]

def test_slice_of_length_zero(setup_teardown_file):
    """Get a slice of length zero from a non-empty dataset."""
    f = setup_teardown_file[3]

    for i, shape in enumerate([(3, ), (2, 2, ), (2,  1, 5)]):
        dset = f.create_dataset('x%d'%i, data=np.zeros(shape, np.int32))
        assert dset.shape == shape
        out = dset[1:1]
        assert isinstance(out, np.ndarray)
        assert out.shape == (0,)+shape[1:]

def test_modify_all(setup_teardown_file):
    f = setup_teardown_file[3]
    dset = f.create_dataset("test", data=np.arange(10))
    dset.data = np.ones(4)
    assert np.all(dset.data == np.ones(4))
