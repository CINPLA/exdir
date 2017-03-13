import pytest
import numpy as np
import quantities as pq

from exdir.core import Attribute
import six

def test_attr_init():
    attribute = Attribute("parent", "mode", "io_mode")

    assert(attribute.parent == "parent")
    assert(attribute.mode == "mode")
    assert(attribute.io_mode == "io_mode")
    assert(attribute.path == [])


# def test_attr_getitem():
#     attr_file = os.path.join(pytest.TESTPATH, "test_attrs")
#     _create_object_directory(attr_file, GROUP_TYPENAME)
#     attribute = Attribute("", Attribute.Mode.ATTRIBUTES, "io_mode")


def test_quantities(setup_teardown_file):
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
    f.attrs['a'] = 4.0
    assert(list(f.attrs.keys()) == ['a'])
    assert(f.attrs['a'] == 4.0)


def test_overwrite(setup_teardown_file):
    """ Attributes are silently overwritten """
    f = setup_teardown_file
    f.attrs['a'] = 4.0
    f.attrs['a'] = 5.0
    assert(f.attrs['a'] == 5.0)


def test_rank(setup_teardown_file):
    """ Attribute rank is preserved """
    f = setup_teardown_file
    f.attrs['a'] = (4.0, 5.0)
    assert(type(f.attrs['a']) == list)
    assert(f.attrs['a'] == [4.0, 5.0])


def test_single(setup_teardown_file):
    """ Attributes of shape (1,) don't become scalars """
    f = setup_teardown_file
    f.attrs['a'] = np.ones((1,))
    out = f.attrs['a']
    assert(type(out) == list)
    assert(out[0] == 1.0)

def test_array(setup_teardown_file):
    """ Attributes of shape (1,) don't become scalars """
    f = setup_teardown_file
    f.attrs['a'] = np.ones((2, 2))
    out = f.attrs['a']
    assert(type(out) == list)
    assert(out == [[1, 1], [1, 1]])

def test_access_exc(setup_teardown_file):
    """ Attempt to access missing item raises KeyError """
    f = setup_teardown_file

    with pytest.raises(KeyError):
        f.attrs['a']



# Deletion of attributes using __delitem__
def test_delete(setup_teardown_file):
    """ Deletion via "del" """
    f = setup_teardown_file

    f.attrs['a'] = 4.0
    assert('a' in f.attrs)
    del f.attrs['a']
    assert('a' not in f.attrs)


def test_delete_exc(setup_teardown_file):
    """ Attempt to delete missing item raises KeyError """
    f = setup_teardown_file
    with pytest.raises(KeyError):
        del f.attrs['a']


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
