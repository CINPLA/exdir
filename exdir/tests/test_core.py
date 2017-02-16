import pytest
import shutil
import exdir
import numpy as np
import os
import quantities as pq
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core import convert_quantities, convert_back_quantities

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
    remove_if_exists()
    # must exist
    for mode in ["r+", "r"]:
        with pytest.raises(IOError):
            f = exdir.File(TESTFILE, mode)
    # create if not exist
    for mode in ["a", "w", "w-"]:
        remove_if_exists()
        f = exdir.File(TESTFILE, mode)
        f.require_dataset('dset', np.arange(10))
        f.attrs['can_overwrite'] = 42
        f.attrs['can_overwrite'] = 14
        f.require_group('mygroup')

    remove_if_exists()
    f = exdir.File(TESTFILE, 'w')
    f.close()# dummy close
    # read write if exist
    f = exdir.File(TESTFILE, "r+")
    f.require_group('mygroup')
    f.require_dataset('dset', np.arange(10))
    # can never overwrite dataset
    with pytest.raises(FileExistsError):
        f.require_dataset('dset', np.arange(10))
    f.attrs['can_overwrite'] = 42
    f.attrs['can_overwrite'] = 14

    # read only, can not write
    f = exdir.File(TESTFILE, 'r')
    with pytest.raises(IOError):
        f.require_dataset('dset', np.arange(10))
        f.attrs['can_not_write'] = 42
        f.create_group('mygroup')

    # can never overwrite dataset
    for mode in ["a", "w", "w-"]:
        remove_if_exists()
        f = exdir.File(TESTFILE, mode)
        f.require_dataset('dset', np.arange(10))
        with pytest.raises(FileExistsError):
            f.require_dataset('dset', np.arange(10))


def test_convert_quantities():
    pq_value = pq.Quantity(1, "m")
    result = convert_quantities(pq_value)
    assert(result == {"value": 1, "unit": "m"})

    pq_value = pq.Quantity([1, 2, 3], "m")
    result = convert_quantities(pq_value)
    assert(result == {"value": [1, 2, 3], "unit": "m"})

    result = convert_quantities(np.array([1, 2, 3]))
    assert(result == [1, 2, 3])

    result = convert_quantities(1)
    assert(result == 1)

    result = convert_quantities(2.3)
    assert(result == 2.3)

    pq_value = pq.UncertainQuantity([1, 2], "m", [3, 4])
    result = convert_quantities(pq_value)
    assert(result == {'unit': 'm', 'uncertainty': [3, 4], 'value': [1.0, 2.0]})


    pq_values = {"quantity": pq.Quantity(1, "m"),
                 "uq_quantity": pq.UncertainQuantity([1, 2], "m", [3, 4])}
    result = convert_quantities(pq_values)
    assert(result == {'quantity': {'unit': 'm', 'value': 1},
                      'uq_quantity': {'unit': 'm', 'uncertainty': [3, 4], 'value': [1.0, 2.0]}})


def test_convert_back_quantities():
    pq_dict = {"value": 1, "unit": "m"}
    result = convert_back_quantities(pq_dict)
    assert(result == pq.Quantity(1, "m"))

    pq_dict = {"value": [1, 2, 3], "unit": "m"}
    result = convert_back_quantities(pq_dict)
    assert(np.array_equal(result, pq.Quantity([1, 2, 3], "m")))

    # Is this wanted behaviour?
    pq_dict = {"value": [1, 2, 3]}
    result = convert_back_quantities(pq_dict)
    assert(result == pq_dict)


    result = convert_back_quantities(1)
    assert(result == 1)

    result = convert_back_quantities(2.3)
    assert(result == 2.3)

    pq_dict = {'unit': 'm', 'uncertainty': [3, 4], 'value': [1.0, 2.0]}
    result = convert_back_quantities(pq_dict)
    pq_value = pq.UncertainQuantity([1, 2], "m", [3, 4])

    assert(isinstance(result, pq.UncertainQuantity))
    assert(result.magnitude.tolist() == pq_value.magnitude.tolist())
    assert(result.dimensionality.string == pq_value.dimensionality.string)
    assert(result.uncertainty.magnitude.tolist() == pq_value.uncertainty.magnitude.tolist())
