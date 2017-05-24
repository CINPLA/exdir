import pytest
import os
import six

from exdir.core import Group, File

# tests for Group class

def test_group_init(setup_teardown_folder):
    group = Group(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert(group.root_directory == pytest.TESTDIR)
    assert(group.object_name == "test_object")
    assert(group.parent_path == "")
    assert(group.io_mode is None)
    assert(group.relative_path == os.path.join("", "test_object"))
    assert(group.name == os.sep + os.path.join("", "test_object"))


# New groups can be created via .create_group method

def test_create_group(setup_teardown_file):
    """ Simple .create_group call """
    f = setup_teardown_file

    grp = f.create_group('foo')
    assert(isinstance(grp, Group))


# TODO update this test when it is implemented
def test_create_intermediate(setup_teardown_file):
    """ Intermediate groups can be created automatically """
    f = setup_teardown_file

    with pytest.raises(NotImplementedError):
        grp = f.create_group('foo/bar/baz')

    # assert(grp.name == '/foo/bar/baz')

def test_create_exception(setup_teardown_file):
    """ Name conflict causes group creation to fail with IOError """
    f = setup_teardown_file

    f.create_group('foo')
    with pytest.raises(IOError):
        f.create_group('foo')


"""
  Feature: Groups can be auto-created, or opened via .require_group
"""

def test_open_existing(setup_teardown_file):
    """ Existing group is opened and returned """
    f = setup_teardown_file

    grp = f.create_group('foo')
    grp2 = f.require_group('foo')
    assert(grp == grp2)


def test_create(setup_teardown_file):
    """ Group is created if it doesn't exist """
    f = setup_teardown_file

    grp = f.require_group('foo')
    assert(isinstance(grp, Group))
    assert(grp.name == '/foo')


def test_require_exception(setup_teardown_file):
    """ Opening conflicting object results in TypeError """
    f = setup_teardown_file
    f.create_dataset('foo', (1,))

    with pytest.raises(TypeError):
        f.require_group('foo')


# TODO uncomment when deletion is implemented
"""
Feature: Objects can be unlinked via "del" operator
"""
# def test_delete(setup_teardown_file):
#     """ Object deletion via "del" """
#
#     f = setup_teardown_file
#     f.create_group('foo')
#     assert('foo' in f)
#     del f['foo']
#     assert('foo' not in f)
#
# def test_nonexisting(setup_teardown_file):
#     """ Deleting non-existent object raises KeyError """
#     f = setup_teardown_file
#
#     with pytest.raises(KeyError):
#         del f['foo']
#
# def test_readonly_delete_exception(setup_teardown_file):
#     """ Deleting object in readonly file raises KeyError """
#     f = setup_teardown_file
#     f.close()
#
#     f = File(pytest.TESTFILE, "r")
#
#     with pytest.raises(KeyError):
#         del f['foo']



"""
    Feature: Objects can be opened via indexing syntax obj[name]
"""

def test_open(setup_teardown_file):
    """ Simple obj[name] opening """
    f = setup_teardown_file

    grp = f.create_group('foo')
    grp2 = f['foo']
    grp3 = f['/foo']

    assert(grp, grp2)
    assert(grp, grp3)


def test_nonexistent(setup_teardown_file):
    """ Opening missing objects raises KeyError """
    f = setup_teardown_file

    with pytest.raises(KeyError):
        f['foo']


        """
              Feature: The Python "in" builtin tests for containership
        """
    def test_contains(self):
    """ "in" builtin works for containership (byte and Unicode) """
    self.f.create_group('a')
    self.assertIn(b'a', self.f)
    self.assertIn(u'a', self.f)
    self.assertIn(b'/a', self.f)
    self.assertIn(u'/a', self.f)
    self.assertNotIn(b'mongoose', self.f)
    self.assertNotIn(u'mongoose', self.f)

    def test_exc(self):
    """ "in" on closed group returns False (see also issue 174) """
    self.f.create_group('a')
    self.f.close()
    self.assertFalse(b'a' in self.f)
    self.assertFalse(u'a' in self.f)

    def test_empty(self):
    """ Empty strings work properly and aren't contained """
    self.assertNotIn(u'', self.f)
    self.assertNotIn(b'', self.f)

    def test_dot(self):
    """ Current group "." is always contained """
    self.assertIn(b'.', self.f)
    self.assertIn(u'.', self.f)

    def test_root(self):
    """ Root group (by itself) is contained """
    self.assertIn(b'/', self.f)
    self.assertIn(u'/', self.f)

    def test_trailing_slash(self):
    """ Trailing slashes are unconditionally ignored """
    self.f.create_group('group')
    self.f['dataset'] = 42
    self.assertIn('/group/', self.f)
    self.assertIn('group/', self.f)
    self.assertIn('/dataset/', self.f)
    self.assertIn('dataset/', self.f)

    def test_softlinks(self):
    """ Broken softlinks are contained, but their members are not """
    self.f.create_group('grp')
    self.f['/grp/soft'] = h5py.SoftLink('/mongoose')
    self.f['/grp/external'] = h5py.ExternalLink('mongoose.hdf5', '/mongoose')
    self.assertIn('/grp/soft', self.f)
    self.assertNotIn('/grp/soft/something', self.f)
    self.assertIn('/grp/external', self.f)
    self.assertNotIn('/grp/external/something', self.f)

    def test_oddball_paths(self):
    """ Technically legitimate (but odd-looking) paths """
    self.f.create_group('x/y/z')
    self.f['dset'] = 42
    self.assertIn('/', self.f)
    self.assertIn('//', self.f)
    self.assertIn('///', self.f)
    self.assertIn('.///', self.f)
    self.assertIn('././/', self.f)
    grp = self.f['x']
    self.assertIn('.//x/y/z', self.f)
    self.assertNotIn('.//x/y/z', grp)
    self.assertIn('x///', self.f)
    self.assertIn('./x///', self.f)
    self.assertIn('dset///', self.f)
    self.assertIn('/dset//', self.f)
