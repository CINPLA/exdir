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

def test_create(setup_teardown_file):
    """ Simple .create_group call """
    f = setup_teardown_file

    grp = f.create_group('foo')
    assert(grp == Group)

def test_create_intermediate(setup_teardown_file):
    """ Intermediate groups can be created automatically """
    f = setup_teardown_file

    grp = f.create_group('foo/bar/baz')
    assert(grp.name == '/foo/bar/baz')

def test_create_exception(setup_teardown_file):
    """ Name conflict causes group creation to fail with ValueError """
    f = setup_teardown_file

    f.create_group('foo')
    with pytest.raises(ValueError):
        f.create_group('foo')

def test_unicode(setup_teardown_file):
    """ Unicode names are correctly stored """
    f = setup_teardown_file

    name = six.u("/Name") + six.unichr(0x4500)
    group = f.create_group(name)
    assert(group.name == name)


# def test_unicode_default(setup_teardown_file):
#     """
#     Unicode names convertible to ASCII are stored as ASCII (issue 239)
#     """
#     f = setup_teardown_file
#
#     name = six.u("/Hello, this is a name")
#     group = f.create_group(name)
#     assert(group.name == name)
