import pytest
import numpy as np
import quantities as pq

from exdir.core import Attribute, File
import six

def test_attr_init():
    attribute = Attribute("parent", "mode", "io_mode")

    assert(attribute.parent == "parent")
    assert(attribute.mode == "mode")
    assert(attribute.io_mode == "io_mode")
    assert(attribute.path == [])



def test_quantities(setup_teardown_file):
    """
    Test if quantities is saved
    """
    f = setup_teardown_file

    f.attrs["temperature"] = 99.0
    assert(f.attrs["temperature"] == 99.0)
    f.attrs["temperature"] = 99.0 * pq.deg
    assert(f.attrs["temperature"] == 99.0 * pq.deg)

    attrs = f.attrs
    assert(type(attrs) is Attribute)


# Attribute creation/retrieval via special methods
def test_create(setup_teardown_file):
    """ Attribute creation by direct assignment """
    f = setup_teardown_file
    f.attrs["a"] = 4.0
    assert(list(f.attrs.keys()) == ["a"])
    assert(f.attrs["a"] == 4.0)


def test_create_dict(setup_teardown_file):
    f = setup_teardown_file

    dictionary = {"a": 1.0, "b": 2.0, "c": 3.0}
    f.attrs["d"] = dictionary

    out = list(f.attrs["d"].items())
    out.sort()
    assert(out == [("a", 1.0), ("b", 2.0), ("c", 3.0)])


def test_to_dict(setup_teardown_file):
    f = setup_teardown_file

    dictionary = {"a": 1.0, "b": 2.0, "c": 3.0}
    f.attrs["d"] = dictionary
    out = f.attrs["d"].to_dict()
    assert(out == dictionary)


def test_number(setup_teardown_file):
    f = setup_teardown_file
    f.attrs[2] = 2
    assert(f.attrs[2] == 2)


def test_overwrite(setup_teardown_file):
    """ Attributes are silently overwritten """
    f = setup_teardown_file
    f.attrs["a"] = 4.0
    f.attrs["a"] = 5.0
    assert(f.attrs["a"] == 5.0)


def test_rank(setup_teardown_file):
    """ Attribute rank is preserved """
    f = setup_teardown_file
    f.attrs["a"] = (4.0, 5.0)
    assert(type(f.attrs["a"]) == list)
    assert(f.attrs["a"] == [4.0, 5.0])


def test_single(setup_teardown_file):
    """ Attributes of shape (1,) don"t become scalars """
    f = setup_teardown_file
    f.attrs["a"] = np.ones((1,))
    out = f.attrs["a"]
    assert(type(out) == list)
    assert(out[0] == 1.0)

def test_array(setup_teardown_file):
    """ Attributes of shape (1,) don"t become scalars """
    f = setup_teardown_file
    f.attrs["a"] = np.ones((2, 2))
    out = f.attrs["a"]
    assert(type(out) == list)
    assert(out == [[1, 1], [1, 1]])




def test_access_exc(setup_teardown_file):
    """ Attempt to access missing item raises KeyError """
    f = setup_teardown_file

    with pytest.raises(KeyError):
        f.attrs["a"]


def test_in(setup_teardown_file):
    """ Test that in (__contains__) works """
    f = setup_teardown_file

    f.attrs["a"] = 4.0
    f.attrs["b"] = 4.0
    f.attrs["c"] = 4.0

    assert("a" in f.attrs)
    assert("b" in f.attrs)
    assert("c" in f.attrs)
    assert("d" not in f.attrs)

def test_keys(setup_teardown_file):
    """ Test that in (__contains__) works """
    f = setup_teardown_file

    f.attrs["a"] = 1.0
    f.attrs["b"] = 2.0
    f.attrs["c"] = 3.0
    out = list(f.attrs.keys())
    out.sort()
    assert(out == ["a", "b", "c"])


def test_values(setup_teardown_file):
    """ Test that in (__contains__) works """
    f = setup_teardown_file

    f.attrs["a"] = 1.0
    f.attrs["b"] = 2.0
    f.attrs["c"] = 3.0
    out = list(f.attrs.values())
    out.sort()
    assert(out == [1.0, 2.0, 3.0])


def test_items(setup_teardown_file):
    """ Test that in (__contains__) works """
    f = setup_teardown_file

    f.attrs["a"] = 1.0
    f.attrs["b"] = 2.0
    f.attrs["c"] = 3.0
    out = list(f.attrs.items())
    out.sort()
    assert(out == [("a", 1.0), ("b", 2.0), ("c", 3.0)])


def test_iter(setup_teardown_file):
    """ Test that in (__contains__) works """
    f = setup_teardown_file

    f.attrs["a"] = 1.0
    f.attrs["b"] = 2.0
    f.attrs["c"] = 3.0

    for i in f.attrs:
        assert(i in ["a", "b", "c"])


# Deletion of attributes using __delitem__
def test_delete(setup_teardown_file):
    """ Deletion via "del" """
    f = setup_teardown_file

    f.attrs["a"] = 4.0
    assert("a" in f.attrs)
    del f.attrs["a"]
    assert("a" not in f.attrs)


def test_delete_exc(setup_teardown_file):
    """ Attempt to delete missing item raises KeyError """
    f = setup_teardown_file
    with pytest.raises(KeyError):
        del f.attrs["a"]




# Attributes can be accessed via Unicode or byte strings

def test_ascii(setup_teardown_file):
    """ Access via pure-ASCII byte string """
    f = setup_teardown_file

    f.attrs[b"ascii"] = 42
    out = f.attrs[b"ascii"]
    assert(out == 42)

def test_raw(setup_teardown_file):
    """ Access via non-ASCII byte string """
    f = setup_teardown_file

    name = b"non-ascii\xfe"
    f.attrs[name] = 42
    out = f.attrs[name]
    assert(out == 42)


def test_unicode(setup_teardown_file):
    """ Access via Unicode string with non-ascii characters """
    f = setup_teardown_file

    name = six.u("Omega") + six.unichr(0x03A9)
    f.attrs[name] = 42
    out = f.attrs[name]
    assert(out == 42)



def test_validity():
    """
    Test that the required functions are implemented.
    """
    Attribute.__len__
    Attribute.__getitem__
    Attribute.__setitem__
    Attribute.__iter__
    Attribute.__delitem__


# All supported types can be stored in attributes


def test_string_scalar(setup_teardown_file):
    """ Storage of variable-length byte string scalars (auto-creation) """
    f = setup_teardown_file

    f.attrs["x"] = b"Hello"
    out = f.attrs["x"]

    assert(out == b"Hello")
    assert(type(out) == bytes)



def test_unicode_scalar(setup_teardown_file):
    """ Storage of variable-length unicode strings (auto-creation) """
    f = setup_teardown_file

    f.attrs["x"] = six.u("Hello") + six.unichr(0x2340) + six.u("!!")
    out = f.attrs["x"]
    assert(out == six.u("Hello") + six.unichr(0x2340) + six.u("!!"))
    assert(type(out) == six.text_type)
