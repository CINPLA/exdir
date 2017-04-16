import pytest
import os
import six

from exdir.core import Group

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
    with pytest.raises(NameError):
        f.create_group('foo')


"""
  Feature: Groups can be auto-created, or opened via .require_group
"""

def test_open_existing(setup_teardown_file):
    """ Existing group is opened and returned """
    f = setup_teardown_file

    grp = f.create_group('foo')
    grp2 = f.require_group('foo')
    # assert(grp == grp2)

def test_create(setup_teardown_file):
    """ Group is created if it doesn't exist """
    f = setup_teardown_file

    grp = f.require_group('foo')
    assert(isinstance(grp, Group))
    assert(grp.name == '/foo')

# def test_require_exception(setup_teardown_file):
#     """ Opening conflicting object results in TypeError """
#     f = setup_teardown_file
#     f.create_dataset('foo', (1,), 'f')
#
#     with pytest.raises(TypeError):
#         f.require_group('foo')
