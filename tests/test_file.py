import pytest
import os


from exdir.core import File, Group
from exdir.core import DATASET_TYPENAME, FILE_TYPENAME
from exdir.core import _create_object_directory, _is_nonraw_object_directory

from conftest import remove


def test_file_init(setup_teardown_folder):
    no_exdir = os.path.join(pytest.TESTPATH, "no_exdir")

    f = File(no_exdir, mode="w")
    f.close()
    assert _is_nonraw_object_directory(no_exdir + ".exdir")
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="w")
    f.close()
    assert _is_nonraw_object_directory(pytest.TESTFILE)
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="a")
    f.close()
    assert _is_nonraw_object_directory(pytest.TESTFILE)
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="a")
    f.close()
    assert _is_nonraw_object_directory(pytest.TESTFILE)
    remove(pytest.TESTFILE)

    os.makedirs(pytest.TESTFILE)
    with pytest.raises(FileExistsError):
        f = File(pytest.TESTFILE, mode="w")

    remove(pytest.TESTFILE)

    _create_object_directory(pytest.TESTFILE, DATASET_TYPENAME)
    with pytest.raises(FileExistsError):
        f = File(pytest.TESTFILE, mode="w")

    remove(pytest.TESTFILE)

    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="r")
    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="r+")

    _create_object_directory(pytest.TESTFILE, FILE_TYPENAME)

    with pytest.raises(FileExistsError):
        f = File(pytest.TESTFILE, mode="w")

    remove(pytest.TESTFILE)

    _create_object_directory(pytest.TESTFILE, FILE_TYPENAME)
    f = File(pytest.TESTFILE, mode="w", allow_remove=True)
    remove(pytest.TESTFILE)

    _create_object_directory(pytest.TESTFILE, FILE_TYPENAME)

    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="w-")

    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="x")

    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="not existing")




def test_file_close(setup_teardown_folder):
    f = File(pytest.TESTFILE, mode="w")
    f.close()


def test_contains(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file
    f.create_group("test")

    assert "/" in  f
    assert "/test" in  f


def test_create_group(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file
    grp = f.create_group("/test")

    assert isinstance(grp, Group)

def test_require_group(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file

    grp = f.require_group("/foo")
    assert isinstance(grp, Group)


def test_open(setup_teardown_file):
    """Simple obj[name] opening."""
    f = setup_teardown_file
    grp = f.create_group("foo")

    grp2 = f["foo"]
    grp3 = f["/foo"]
    fid = f["/"]

    assert grp == grp2
    assert grp2 == grp3
    assert f == fid


# TODO test naming rules, strict and so on

# TODO Creating these tests
# def test_create(self):
#     """ Mode 'w' opens file in overwrite mode """
#     fname = self.mktemp()
#     fid = File(fname, 'w')
#     self.assertTrue(fid)
#     fid.create_group('foo')
#     fid.close()
#     fid = File(fname, 'w')
#     self.assertNotIn('foo', fid)
#     fid.close()

# def test_create_exclusive(self):
#     """ Mode 'w-' opens file in exclusive mode """
#     fname = self.mktemp()
#     fid = File(fname, 'w-')
#     self.assert_(fid)
#     fid.close()
#     with self.assertRaises(IOError):
#         File(fname, 'w-')

# def test_append(self):
#     """ Mode 'a' opens file in append/readwrite mode, creating if necessary """
#     fname = self.mktemp()
#     fid = File(fname, 'a')
#     try:
#         self.assert_(fid)
#         fid.create_group('foo')
#         self.assert_('foo' in fid)
#     finally:
#         fid.close()
#     fid = File(fname, 'a')
#     try:
#         self.assert_('foo' in fid)
#         fid.create_group('bar')
#         self.assert_('bar' in fid)
#     finally:
#         fid.close()

# def test_readonly(self):
#     """ Mode 'r' opens file in readonly mode """
#     fname = self.mktemp()
#     fid = File(fname, 'w')
#     fid.close()
#     self.assert_(not fid)
#     fid = File(fname, 'r')
#     self.assert_(fid)
#     with self.assertRaises(ValueError):
#         fid.create_group('foo')
#     fid.close()

# def test_readwrite(self):
#     """ Mode 'r+' opens existing file in readwrite mode """
#     fname = self.mktemp()
#     fid = File(fname, 'w')
#     fid.create_group('foo')
#     fid.close()
#     fid = File(fname, 'r+')
#     self.assert_('foo' in fid)
#     fid.create_group('bar')
#     self.assert_('bar' in fid)
#     fid.close()

# def test_nonexistent_file(self):
#     """ Modes 'r' and 'r+' do not create files """
#     fname = self.mktemp()
#     with self.assertRaises(IOError):
#         File(fname, 'r')
#     with self.assertRaises(IOError):
#         File(fname, 'r+')

# def test_invalid_mode(self):
#     """ Invalid modes raise ValueError """
#     with self.assertRaises(ValueError):
# File(self.mktemp(), 'mongoose')


# TODO uncomment when enter and exit has been implemented
# # Feature: File objects can be used as context managers
# def test_context_manager(setup_teardown_folder):
#     """File objects can be used in with statements."""

#     no_exdir = os.path.join(pytest.TESTPATH, "no_exdir")

#     with File(no_exdir, mode="w") as f:
#         assert f

#     assert not f