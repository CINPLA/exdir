import pytest
import exdir
import numpy as np
import os
import quantities as pq


from exdir.core import *
from exdir.core import _assert_valid_name, _create_object_directory
from exdir.core import _metafile_from_directory, _is_nonraw_object_directory

from conftest import remove


def test_modify_view(setup_teardown_file):
    f = setup_teardown_file
    dataset = f.create_dataset("mydata", data=np.array([1, 2, 3, 4, 5, 6, 7, 8]))
    dataset[3:5] = np.array([8, 9])
    assert(np.array_equal(f["mydata"][3:5], np.array([8, 9])))
    view = dataset[3:5]
    view[0] = 10
    assert(f["mydata"][3] == 10)


def test_dataset(setup_teardown_file):
    f = setup_teardown_file

    a = np.array([1, 2, 3, 4, 5])
    dset = f.require_dataset("mydata", data=a)

    dset[1:3] = 8.0
    assert(np.array_equal(f["mydata"].data, np.array([1, 8, 8, 4, 5])))
    assert(f["mydata"][2] == 8)

    group = f.require_group("mygroup")
    b = np.array([[1, 2, 3], [4, 5, 6]])
    dset2 = group.require_dataset("some_data", b)
    c = np.zeros((2, 3, 4))
    group.require_dataset("some_data2", c)

    assert(c.shape == (2, 3, 4))
    assert(group["some_data"][()].shape == (2, 3))


def test_attrs(setup_teardown_file):
    f = setup_teardown_file

    f.attrs["temperature"] = 99.0
    assert(f.attrs["temperature"] == 99.0)
    f.attrs["temperature"] = 99.0 * pq.deg
    assert(f.attrs["temperature"] == 99.0 * pq.deg)

    attrs = f.attrs
    assert(type(attrs) is exdir.core.Attribute)

    attrs["test"] = {
        "name": "temp",
        "value": 19
    }
    assert("test" in f.attrs)
    assert(type(f.attrs["test"]) is exdir.core.Attribute)
    assert(dict(f.attrs["test"]) == {"name": "temp", "value": 19})


def test_open_file(setup_teardown_folder):
    for mode in ["a", "r", "r+"]:
        f = exdir.File(pytest.TESTFILE, mode)
        f.close()
        assert(os.path.exists(pytest.TESTFILE))

    # invalid file
    dummy_file = "/tmp/dummy.exdir"
    if not os.path.exists(dummy_file):
        os.mkdir(dummy_file)
    for mode in ["a", "r", "r+", "w", "w-"]:
        with pytest.raises(FileExistsError):
            f = exdir.File(dummy_file)

    # truncate
    f = exdir.File(pytest.TESTFILE)
    f.create_group("test_group")
    assert("test_group" in f)
    f.close()
    f = exdir.File(pytest.TESTFILE, "w", allow_remove=True)
    assert("test_group" not in f)
    f.close()
    assert(os.path.exists(pytest.TESTFILE))

    # assume doesn't exist
    remove(pytest.TESTFILE)
    f = exdir.File(pytest.TESTFILE, "w-")
    f.close()
    assert(os.path.exists(pytest.TESTFILE))


def test_naming_rule_simple(setup_teardown_folder):
    f = exdir.File(pytest.TESTFILE, naming_rule='simple')
    grp = f.require_group('sdf')
    with pytest.raises(NameError):
        grp1 = f.require_group('Sdf')
    grp2 = grp.require_group('Abs')
    with pytest.raises(NameError):
        grp3 = grp.require_group('abs')
    d = f.require_dataset('sdff')
    with pytest.raises(NameError):
        d1 = f.require_dataset('Sdff')
    d2 = grp.require_dataset('Abss')
    with pytest.raises(NameError):
        d3 = grp.require_dataset('abss')


def test_open_mode(setup_teardown_folder):
    # must exist
    for mode in ["r+", "r"]:
        with pytest.raises(IOError):
            f = exdir.File(pytest.TESTFILE, mode)
    # create if not exist
    for mode in ["a", "w", "w-"]:
        remove(pytest.TESTFILE)
        f = exdir.File(pytest.TESTFILE, mode)
        f.require_dataset('dset', np.arange(10))
        f.attrs['can_overwrite'] = 42
        f.attrs['can_overwrite'] = 14
        f.require_group('mygroup')

    remove(pytest.TESTFILE)
    f = exdir.File(pytest.TESTFILE, 'w')
    f.close()  # dummy close
    # read write if exist
    f = exdir.File(pytest.TESTFILE, "r+")
    f.require_group('mygroup')
    f.require_dataset('dset', np.arange(10))
    f.attrs['can_overwrite'] = 42
    f.attrs['can_overwrite'] = 14

    # read only, can not write
    f = exdir.File(pytest.TESTFILE, 'r')
    with pytest.raises(IOError):
        f.require_dataset('dset', np.arange(10))
        f.attrs['can_not_write'] = 42
        f.create_group('mygroup')


# tests for File class
def test_file_init(setup_teardown_folder):
    no_exdir = os.path.join(pytest.TESTPATH, "no_exdir")

    f = File(no_exdir, mode="w")
    f.close()
    assert(_is_nonraw_object_directory(no_exdir + ".exdir"))
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="w")
    f.close()
    assert(_is_nonraw_object_directory(pytest.TESTFILE))
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="a")
    f.close()
    assert(_is_nonraw_object_directory(pytest.TESTFILE))
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="a")
    f.close()
    assert(_is_nonraw_object_directory(pytest.TESTFILE))
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


def test_file_close(setup_teardown_folder):
    f = File(pytest.TESTFILE, mode="w")
    f.close()


# tests for Attribute class

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

# tests for Group class
def test_group_init(setup_teardown_folder):
    group = Group(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert(group.root_directory == pytest.TESTDIR)
    assert(group.object_name == "test_object")
    assert(group.parent_path == "")
    assert(group.io_mode is None)
    assert(group.relative_path == os.path.join("", "test_object"))
    assert(group.name == os.sep + os.path.join("", "test_object"))
