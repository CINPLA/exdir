import pytest
import shutil
import exdir
import numpy as np
import os
import quantities as pq


from exdir.core import *
from exdir.core import _assert_valid_name, _create_object_directory
from exdir.core import _metafile_from_directory, _is_valid_object_directory


filepath = os.path.abspath(__file__)
filedir = os.path.dirname(filepath)

testmaindir = ".expipe_test_dir_Aegoh4ahlaechohV5ooG9vew1yahDe2d"
TESTPATH = os.path.join(filedir, testmaindir)
TESTDIR = os.path.join(TESTPATH, "expipe_dir")
TESTFILE = os.path.join(TESTPATH, "test.exdir")



@pytest.fixture
def folderhandling():
    if os.path.exists(TESTPATH):
        shutil.rmtree(TESTPATH)
        assert(not os.path.exists(TESTPATH))

    os.makedirs(TESTPATH)

    yield

    if os.path.exists(TESTPATH):
        shutil.rmtree(TESTPATH)
        assert(not os.path.exists(TESTPATH))


def remove_testfile():
    if os.path.exists(TESTFILE):
        shutil.rmtree(TESTFILE)
    assert(not os.path.exists(TESTFILE))


def remove_testdir():
    if os.path.exists(TESTDIR):
        shutil.rmtree(TESTDIR)
    assert(not os.path.exists(TESTDIR))



def test_modify_view(folderhandling):
    f = exdir.File(TESTFILE, mode="w", allow_remove=True)
    dataset = f.create_dataset("mydata", data=np.array([1, 2, 3, 4, 5, 6, 7, 8]))
    dataset[3:5] = np.array([8, 9])
    assert(np.array_equal(f["mydata"][3:5], np.array([8, 9])))
    view = dataset[3:5]
    view[0] = 10
    assert(f["mydata"][3] == 10)


def test_dataset(folderhandling):
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


def test_attrs(folderhandling):
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


def test_open_file(folderhandling):
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
    remove_testfile()
    f = exdir.File(TESTFILE, "w-")
    f.close()
    assert(os.path.exists(TESTFILE))


def test_open_mode(folderhandling):
    # must exist
    for mode in ["r+", "r"]:
        with pytest.raises(IOError):
            f = exdir.File(TESTFILE, mode)
    # create if not exist
    for mode in ["a", "w", "w-"]:
        remove_testfile()
        f = exdir.File(TESTFILE, mode)
        f.require_dataset('dset', np.arange(10))
        f.attrs['can_overwrite'] = 42
        f.attrs['can_overwrite'] = 14
        f.require_group('mygroup')

    remove_testfile()
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
        remove_testfile()
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


    pq_values = {"list": [1, 2, 3], "quantity": pq.Quantity(1, "m")}
    pq_dict = {"list": [1, 2, 3], "quantity": {'unit': 'm', 'value': 1}}
    result = convert_quantities(pq_values)
    assert(result == pq_dict)


def test_convert_back_quantities():
    pq_dict = {"value": 1, "unit": "m"}
    result = convert_back_quantities(pq_dict)
    assert(result == pq.Quantity(1, "m"))


    pq_dict = {"value": [1, 2, 3], "unit": "m"}
    result = convert_back_quantities(pq_dict)
    assert(np.array_equal(result, pq.Quantity([1, 2, 3], "m")))


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



    pq_dict = {'quantity': {'unit': 'm', 'value': 1},
               'uq_quantity': {'unit': 'm', 'uncertainty': [3, 4], 'value': [1.0, 2.0]}}
    pq_values = {"quantity": pq.Quantity(1, "m"),
                 "uq_quantity": pq.UncertainQuantity([1, 2], "m", [3, 4])}
    result = convert_back_quantities(pq_values)
    assert(result == pq_values)



    pq_values = {"list": [1, 2, 3], "quantity": {'unit': 'm', 'value': 1}}
    result = convert_back_quantities(pq_values)
    assert(result == {"list": [1, 2, 3], "quantity": pq.Quantity(1, "m")})


def test_assert_valid_name():
    valid_name = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY" +
                  "Z1234567890_ ")

    _assert_valid_name(valid_name)

    invalid_name = ""
    with pytest.raises(NameError):
        _assert_valid_name(invalid_name)

    invalid_name = "-"
    with pytest.raises(NameError):
        _assert_valid_name(invalid_name)

    with pytest.raises(NameError):
        _assert_valid_name(META_FILENAME)

    with pytest.raises(NameError):
        _assert_valid_name(ATTRIBUTES_FILENAME)

    with pytest.raises(NameError):
        _assert_valid_name(RAW_FOLDER_NAME)


def test_create_object_directory(folderhandling):
    with pytest.raises(ValueError):
        _create_object_directory(TESTDIR, "wrong_typename")

    _create_object_directory(TESTDIR, DATASET_TYPENAME)

    assert(os.path.isdir(TESTDIR))

    file_path = os.path.join(TESTDIR, META_FILENAME)
    assert(os.path.isfile(file_path))

    compare_metadata = {
        EXDIR_METANAME: {
            TYPE_METANAME: DATASET_TYPENAME,
            VERSION_METANAME: 1}
    }

    with open(file_path, "r") as meta_file:
        metadata = yaml.safe_load(meta_file)

        assert(metadata == compare_metadata)


    with pytest.raises(IOError):
        _create_object_directory(TESTDIR, DATASET_TYPENAME)


def test_metafile_from_directory(folderhandling):
    compare_metafile = os.path.join(TESTPATH, META_FILENAME)
    with open(compare_metafile, 'w') as f:
        pass

    metafile = _metafile_from_directory(TESTPATH)

    assert(metafile == compare_metafile)


def test_is_valid_object_directory(folderhandling):
    os.makedirs(TESTDIR)

    result = _is_valid_object_directory(TESTDIR)
    assert(result is False)

    compare_metafile = os.path.join(TESTDIR, META_FILENAME)
    with open(compare_metafile, 'w') as f:
        pass

    result = _is_valid_object_directory(TESTDIR)
    assert(result is False)


    remove_testfile()
    with open(compare_metafile, "w") as meta_file:
        metadata = {
            EXDIR_METANAME: {
                VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)

    result = _is_valid_object_directory(TESTDIR)
    assert(result is False)


    remove_testfile()
    with open(compare_metafile, "w") as meta_file:
        metadata = {
            EXDIR_METANAME: {
                TYPE_METANAME: "wrong_typename",
                VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)

    result = _is_valid_object_directory(TESTDIR)
    assert(result is False)

    remove_testfile()
    with open(compare_metafile, "w") as meta_file:
        metadata = {
            EXDIR_METANAME: {
                TYPE_METANAME: DATASET_TYPENAME,
                VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)

    result = _is_valid_object_directory(TESTDIR)
    assert(result is True)

    remove_testdir()

    _create_object_directory(TESTDIR, DATASET_TYPENAME)
    result = _is_valid_object_directory(TESTDIR)
    assert(result is True)


# def test_ObjectInit():
#     testObject = Object()


def test_attr_init():
    attribute = Attribute("parent", "mode", "io_mode")

    assert(attribute.parent == "parent")
    assert(attribute.mode == "mode")
    assert(attribute.io_mode == "io_mode")
    assert(attribute.path == [])
