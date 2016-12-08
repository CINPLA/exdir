import pytest
import shutil
import eds
import numpy as np
import os

TESTFILE = "/tmp/test.eds"


def remove_if_exists():
    if os.path.exists(TESTFILE):
        shutil.rmtree(TESTFILE)
    assert(not os.path.exists(TESTFILE))


def test_everything():
    remove_if_exists()
    f = eds.File(TESTFILE)
    f.attrs["temperature"] = 99.0
    print(f.attrs["temperature"])

    a = np.array([1, 2, 3, 4, 5])
    dset = f.require_dataset("mydata", data=a)

    dset[1:3] = 8.0

    print(f["mydata"][()])

    print(f["mydata"][2])

    group = f.require_group("mygroup")

    b = np.array([[1, 2, 3], [4, 5, 6]])
    dset2 = group.require_dataset("some_data", b)
    c = np.array([[[[1,2,3],[4,5,6]]],[[[7,8,9],[0,1,2]]],
                  [[[2,4,1],[5,5,1]]],[[[1,2,1],[1,3,2]]]])
    group.require_dataset("some_data2", c)
    print(c.shape)
        
    print(group["some_data"][()])


def test_open_file():    
    remove_if_exists()
    for mode in ["a", "r", "r+"]:
        f = eds.File(TESTFILE, mode)
        f.close()
        assert(os.path.exists(TESTFILE))
    
    # invalid file
    dummy_file = "/tmp/dummy.eds"
    if not os.path.exists(dummy_file):
        os.mkdir(dummy_file)
    for mode in ["a", "r", "r+", "w", "w-"]:
        with pytest.raises(FileExistsError):
            f = eds.File(dummy_file)
    
    # truncate
    f = eds.File(TESTFILE, "w")
    f.create_group("test_group")
    assert("test_group" in f)
    f.close()
    f = eds.File(TESTFILE, "w")
    assert("test_group" not in f)
    f.close()
    assert(os.path.exists(TESTFILE))
    
    # assume doesn't exist
    remove_if_exists()
    f = eds.File(TESTFILE, "w-")
    f.close()
    
    assert(os.path.exists(TESTFILE))
