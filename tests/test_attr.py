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
try:
    import ruamel_yaml as yaml
except ImportError:
    import ruamel.yaml as yaml

from exdir.core import Attribute, File
import six

def test_attr_init():
    attribute = Attribute("parent", "mode", "file")

    assert attribute.parent == "parent"
    assert attribute.mode == "mode"
    assert attribute.file == "file"
    assert attribute.path == []

# Attribute creation/retrieval via special methods
def test_create(setup_teardown_file):
    """Attribute creation by direct assignment."""
    f = setup_teardown_file[3]
    f.attrs["a"] = 4.0
    assert list(f.attrs.keys()) == ["a"]
    assert f.attrs["a"] == 4.0


def test_create_dict(setup_teardown_file):
    f = setup_teardown_file[3]

    dictionary = {"a": 1.0, "b": 2.0, "c": 3.0}
    f.attrs["d"] = dictionary

    out = list(f.attrs["d"].items())
    out.sort()
    assert out == [("a", 1.0), ("b", 2.0), ("c", 3.0)]


def test_to_dict(setup_teardown_file):
    f = setup_teardown_file[3]

    dictionary = {"a": 1.0, "b": 2.0, "c": 3.0}
    f.attrs["d"] = dictionary
    out = f.attrs["d"].to_dict()
    assert out == dictionary


def test_number(setup_teardown_file):
    f = setup_teardown_file[3]
    f.attrs[2] = 2
    assert f.attrs[2] == 2


def test_overwrite(setup_teardown_file):
    """Attributes are silently overwritten."""
    f = setup_teardown_file[3]
    f.attrs["a"] = 4.0
    f.attrs["a"] = 5.0
    assert f.attrs["a"] == 5.0


def test_rank(setup_teardown_file):
    """Attribute rank is preserved."""
    f = setup_teardown_file[3]
    f.attrs["a"] = (4.0, 5.0)
    assert type(f.attrs["a"]) == list
    assert f.attrs["a"] == [4.0, 5.0]


def test_single(setup_teardown_file):
    """Numpy arrays as attribute gives errors."""
    f = setup_teardown_file[3]

    with pytest.raises(yaml.representer.RepresenterError):
        f.attrs["a"] = np.ones((1,))

def test_array(setup_teardown_file):
    """Numpy arrays as attribute gives errors."""
    f = setup_teardown_file[3]

    with pytest.raises(yaml.representer.RepresenterError):
        f.attrs["a"] = np.ones((2, 2))




def test_access_exc(setup_teardown_file):
    """Attempt to access missing item raises KeyError."""
    f = setup_teardown_file[3]

    with pytest.raises(KeyError):
        f.attrs["a"]


def test_in(setup_teardown_file):
    """Test that in (__contains__) works."""
    f = setup_teardown_file[3]

    f.attrs["a"] = 4.0
    f.attrs["b"] = 4.0
    f.attrs["c"] = 4.0

    assert "a" in f.attrs
    assert "b" in f.attrs
    assert "c" in f.attrs
    assert "d" not in f.attrs

def test_keys(setup_teardown_file):
    """Test that in (__contains__) works."""
    f = setup_teardown_file[3]

    f.attrs["a"] = 1.0
    f.attrs["b"] = 2.0
    f.attrs["c"] = 3.0
    out = list(f.attrs.keys())
    out.sort()
    assert out == ["a", "b", "c"]


def test_values(setup_teardown_file):
    """Test that in (__contains__) works."""
    f = setup_teardown_file[3]

    f.attrs["a"] = 1.0
    f.attrs["b"] = 2.0
    f.attrs["c"] = 3.0
    out = list(f.attrs.values())
    out.sort()
    assert out == [1.0, 2.0, 3.0]


def test_items(setup_teardown_file):
    """Test that in (__contains__) works."""
    f = setup_teardown_file[3]

    f.attrs["a"] = 1.0
    f.attrs["b"] = 2.0
    f.attrs["c"] = 3.0
    out = list(f.attrs.items())
    out.sort()
    assert out == [("a", 1.0), ("b", 2.0), ("c", 3.0)]


def test_iter(setup_teardown_file):
    """Test that in (__contains__) works."""
    f = setup_teardown_file[3]

    f.attrs["a"] = 1.0
    f.attrs["b"] = 2.0
    f.attrs["c"] = 3.0

    for i in f.attrs:
        assert i in ["a", "b", "c"]


# TODO uncomment as soon as __del__ is implemented
# Deletion of attributes using __delitem__
# def test_delete(setup_teardown_file):
#     """Deletion via "del"."""
#     f = setup_teardown_file[3]
#
#     f.attrs["a"] = 4.0
#     assert "a" in f.attrs
#     del f.attrs["a"]
#     assert "a" not in f.attrs
#
#
# def test_delete_exc(setup_teardown_file):
#     """Attempt to delete missing item raises KeyError."""
#     f = setup_teardown_file[3]
#     with pytest.raises(KeyError):
#         del f.attrs["a"]




# Attributes can be accessed via Unicode or byte strings

def test_ascii(setup_teardown_file):
    """Access via pure-ASCII byte string."""
    f = setup_teardown_file[3]

    f.attrs[b"ascii"] = 42
    out = f.attrs[b"ascii"]
    assert out == 42

# TODO verify that we don't want to support non-ASCII byte strings
# NOTE fails with Python 2.7
# def test_raw(setup_teardown_file):
    # """Access via non-ASCII byte string."""
    # f = setup_teardown_file[3]

    # name = b"non-ascii\xfe"
    # f.attrs[name] = 42
    # out = f.attrs[name]
    # assert out == 42


def test_unicode(setup_teardown_file):
    """Access via Unicode string with non-ascii characters."""
    f = setup_teardown_file[3]

    name = six.u("Omega") + six.unichr(0x03A9)
    f.attrs[name] = 42
    out = f.attrs[name]
    assert out == 42



def test_validity():
    """
    Test that the required functions are implemented.
    """
    Attribute.__len__
    Attribute.__getitem__
    Attribute.__setitem__
    Attribute.__iter__
    # TODO uncomment as soon as __del__ is implemented
    # Attribute.__delitem__


# All supported types can be stored in attributes


def test_string_scalar(setup_teardown_file):
    """Storage of variable-length byte string scalars (auto-creation)."""
    f = setup_teardown_file[3]

    f.attrs["x"] = b"Hello"
    out = f.attrs["x"]

    assert out == b"Hello"
    assert type(out) == bytes



def test_unicode_scalar(setup_teardown_file):
    """Storage of variable-length unicode strings (auto-creation)."""
    f = setup_teardown_file[3]

    f.attrs["x"] = six.u("Hello") + six.unichr(0x2340) + six.u("!!")
    out = f.attrs["x"]
    assert out == six.u("Hello") + six.unichr(0x2340) + six.u("!!")
    assert type(out) == six.text_type


def test_attrs(setup_teardown_file):
    f = setup_teardown_file[3]

    f.attrs["temperature"] = 99.0
    assert f.attrs["temperature"] == 99.0

    attrs = f.attrs
    assert type(attrs) is Attribute

    attrs["test"] = {
        "name": "temp",
        "value": 19
    }
    assert "test" in f.attrs
    assert type(f.attrs["test"]) is Attribute
    assert dict(f.attrs["test"]) == {"name": "temp", "value": 19}




# TODO uncomment and use these tests if we allows for all attribute information
#      to be saved
# # Feature: Scalar types map correctly to array scalars

# def test_int(setup_teardown_file):
#     """Integers are read as correct NumPy type."""
#     f = setup_teardown_file[3]

#     f.attrs['x'] = np.array(1, dtype=np.int8)
#     out = f.attrs['x']
#     print (out)
#     assert isinstance(out, np.int8)

# def test_compound(setup_teardown_file):
#     """Compound scalars are read as numpy.void."""
#     f = setup_teardown_file[3]

#     dt = np.dtype([('a', 'i'), ('b', 'f')])
#     data = np.array((1, 4.2), dtype=dt)
#     f.attrs['x'] = data
#     out = f.attrs['x']
#     assert isinstance(out, np.void)
#     assert out == data
#     assert out['b'] == data['b']

# # Feature: Non-scalar types are correctly retrieved as ndarrays

# def test_single_array(setup_teardown_file):
#     """Single-element arrays are correctly recovered."""
#     f = setup_teardown_file[3]

#     data = np.ndarray((1,), dtype='f')
#     f.attrs['x'] = data
#     out = f.attrs['x']
#     assert isinstance(out, np.ndarray)
#     assert out.shape == (1,)

# def test_multi_array(setup_teardown_file):
#     """Rank-1 arrays are correctly recovered."""
#     f = setup_teardown_file[3]

#     data = np.ndarray((42,), dtype='f')
#     data[:] = 42.0
#     data[10:35] = -47.0
#     f.attrs['x'] = data
#     out = f.attrs['x']
#     assert isinstance(out, np.ndarray)
#     assert out.shape == (42,)
#     assert np.array_equal(out, data)


# # Feature: All supported types can be stored in attributes

# def test_int_all(setup_teardown_file):
#     """Storage of integer types."""
#     f = setup_teardown_file[3]

#     dtypes = (np.int8, np.int16, np.int32, np.int64,
#               np.uint8, np.uint16, np.uint32, np.uint64)
#     for dt in dtypes:
#         data = np.ndarray((1,), dtype=dt)
#         data[...] = 42
#         f.attrs['x'] = data
#         out = f.attrs['x']
#         assert out.dtype == dt
#         assert np.array_equal(out, data)

# def test_float(setup_teardown_file):
#     """Storage of floating point types."""
#     f = setup_teardown_file[3]

#     dtypes = tuple(np.dtype(x) for x in ('<f4', '>f4', '<f8', '>f8'))

#     for dt in dtypes:
#         data = np.ndarray((1,), dtype=dt)
#         data[...] = 42.3
#         f.attrs['x'] = data
#         out = f.attrs['x']
#         assert out.dtype == dt
#         assert np.array_equal(out, data)

# def test_complex(setup_teardown_file):
#     """Storage of complex types."""
#     f = setup_teardown_file[3]

#     dtypes = tuple(np.dtype(x) for x in ('<c8', '>c8', '<c16', '>c16'))

#     for dt in dtypes:
#         data = np.ndarray((1,), dtype=dt)
#         data[...] = -4.2j+35.9
#         f.attrs['x'] = data
#         out = f.attrs['x']
#         assert out.dtype == dt
#         assert np.array_equal(out, data)

# def test_string(setup_teardown_file):
#     """Storage of fixed-length strings."""
#     f = setup_teardown_file[3]

#     dtypes = tuple(np.dtype(x) for x in ('|S1', '|S10'))

#     for dt in dtypes:
#         data = np.ndarray((1,), dtype=dt)
#         data[...] = 'h'
#         f.attrs['x'] = data
#         out = f.attrs['x']
#         assert out.dtype == dt
#         assert out[0] == data[0]

# def test_bool(setup_teardown_file):
#     """Storage of NumPy booleans."""
#     f = setup_teardown_file[3]

#     data = np.ndarray((2,), dtype=np.bool_)
#     data[...] = True, False
#     f.attrs['x'] = data
#     out = f.attrs['x']
#     assert out.dtype == data.dtype
#     assert out[0] == data[0]
#     assert out[1] == data[1]
