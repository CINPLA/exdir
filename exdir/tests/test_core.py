import pytest
import shutil
import exdir
import numpy as np
import os
import quantities as pq

TESTFILE = "/tmp/test_Aegoh4ahlaechohV5ooG9vew1yahDe2d.exdir"


def remove_if_exists():
    if os.path.exists(TESTFILE):
        shutil.rmtree(TESTFILE)
    assert(not os.path.exists(TESTFILE))


def test_modify_view():
    f = exdir.File(TESTFILE, mode="w", allow_remove=True)
    dataset = f.create_dataset("mydata", data=np.array([1, 2, 3, 4, 5, 6, 7, 8]))
    dataset[3:5] = np.array([8, 9])
    assert(np.array_equal(f["mydata"][3:5], np.array([8, 9])))
    view = dataset[3:5]
    view[0] = 10
    assert(f["mydata"][3] == 10)


def test_dataset():
    f = exdir.File(TESTFILE, mode="w", allow_remove=True)
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


def test_attrs():
    f = exdir.File(TESTFILE, mode="w", allow_remove=True)
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


def test_open_file():
    remove_if_exists()
    for mode in ["a", "r", "r+"]:
        f = exdir.File(TESTFILE, mode)
        f.close()
        assert(os.path.exists(TESTFILE))
    
    # invalid file
    dummy_file = "/tmp/dummy.exdir"
    if not os.path.exists(dummy_file):
        os.mkdir(dummy_file)
    for mode in ["a", "r", "r+", "w", "w-"]:
        with pytest.raises(FileExistsError):
            f = exdir.File(dummy_file)

    # truncate
    f = exdir.File(TESTFILE)
    f.create_group("test_group")
    assert("test_group" in f)
    f.close()
    f = exdir.File(TESTFILE, "w", allow_remove=True)
    assert("test_group" not in f)
    f.close()
    assert(os.path.exists(TESTFILE))

    # assume doesn't exist
    remove_if_exists()
    f = exdir.File(TESTFILE, "w-")
    f.close()
    assert(os.path.exists(TESTFILE))


def test_open_mode():
    for mode in ["a", "w", "w-"]:
        remove_if_exists()
        f = exdir.File(TESTFILE, mode)
        f.require_dataset('dset', np.arange(10))
        f.attrs = 'can write attr'

    f = exdir.File(TESTFILE, "r+")
    f.require_dataset('dset', np.arange(10))
    f.attrs = 'can write attr'

    f = exdir.File(TESTFILE, 'r')
    with pytest.raises(IOError):
        f.require_dataset('dset', np.arange(10))
        f.attrs = 'cannot write attr'
