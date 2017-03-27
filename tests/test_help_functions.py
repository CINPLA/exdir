import pytest
import os
import six

from exdir.core import *
from exdir.core import _assert_valid_name, _create_object_directory
from exdir.core import _metafile_from_directory, _is_nonraw_object_directory

from conftest import remove

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
    assert(result == {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]})


    pq_values = {"quantity": pq.Quantity(1, "m"),
                 "uq_quantity": pq.UncertainQuantity([1, 2], "m", [3, 4])}
    result = convert_quantities(pq_values)
    assert(result == {"quantity": {"unit": "m", "value": 1},
                      "uq_quantity": {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}})


    pq_values = {"list": [1, 2, 3], "quantity": pq.Quantity(1, "m")}
    pq_dict = {"list": [1, 2, 3], "quantity": {"unit": "m", "value": 1}}
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


    pq_dict = {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}
    result = convert_back_quantities(pq_dict)
    pq_value = pq.UncertainQuantity([1, 2], "m", [3, 4])

    assert(isinstance(result, pq.UncertainQuantity))
    assert(result.magnitude.tolist() == pq_value.magnitude.tolist())
    assert(result.dimensionality.string == pq_value.dimensionality.string)
    assert(result.uncertainty.magnitude.tolist() == pq_value.uncertainty.magnitude.tolist())



    pq_dict = {"quantity": {"unit": "m", "value": 1},
               "uq_quantity": {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}}
    pq_values = {"quantity": pq.Quantity(1, "m"),
                 "uq_quantity": pq.UncertainQuantity([1, 2], "m", [3, 4])}
    result = convert_back_quantities(pq_values)
    assert(result == pq_values)



    pq_values = {"list": [1, 2, 3], "quantity": {"unit": "m", "value": 1}}
    result = convert_back_quantities(pq_values)
    assert(result == {"list": [1, 2, 3], "quantity": pq.Quantity(1, "m")})


def test_assert_valid_name():
    _assert_valid_name("abcdefghijklmnopqrstuvwxyz1234567890_-")
    with pytest.raises(NameError):
        _assert_valid_name("")

    _assert_valid_name("A")

    with pytest.raises(NameError):
        _assert_valid_name("\n")

    with pytest.raises(NameError):
        _assert_valid_name(six.unichr(0x4500))

    with pytest.raises(NameError):
        _assert_valid_name(META_FILENAME)

    with pytest.raises(NameError):
        _assert_valid_name(ATTRIBUTES_FILENAME)

    with pytest.raises(NameError):
        _assert_valid_name(RAW_FOLDER_NAME)

def test_assert_valid_name_no_strict():
    valid_name = ("abcdefghijklmnopqrstuvwxyz1234567890_-")

    _assert_valid_name(valid_name, "none")

    invalid_name = " "
    _assert_valid_name(invalid_name, "none")

    invalid_name = "A"
    _assert_valid_name(invalid_name, "none")

    invalid_name = "\n"
    _assert_valid_name(invalid_name, "none")


    invalid_name = six.unichr(0x4500)
    _assert_valid_name(invalid_name, "none")


    with pytest.raises(NameError):
        _assert_valid_name(META_FILENAME, "none")

    with pytest.raises(NameError):
        _assert_valid_name(ATTRIBUTES_FILENAME, "none")

    with pytest.raises(NameError):
        _assert_valid_name(RAW_FOLDER_NAME, "none")



def test_create_object_directory(setup_teardown_folder):
    with pytest.raises(ValueError):
        _create_object_directory(pytest.TESTDIR, "wrong_typename")

    _create_object_directory(pytest.TESTDIR, DATASET_TYPENAME)

    assert(os.path.isdir(pytest.TESTDIR))

    file_path = os.path.join(pytest.TESTDIR, META_FILENAME)
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
        _create_object_directory(pytest.TESTDIR, DATASET_TYPENAME)


def test_metafile_from_directory(setup_teardown_folder):
    compare_metafile = os.path.join(pytest.TESTPATH, META_FILENAME)
    with open(compare_metafile, "w") as f:
        pass

    metafile = _metafile_from_directory(pytest.TESTPATH)

    assert(metafile == compare_metafile)


def test_is_nonraw_object_directory(setup_teardown_folder):
    os.makedirs(pytest.TESTDIR)

    result = _is_nonraw_object_directory(pytest.TESTDIR)
    assert(result is False)

    compare_metafile = os.path.join(pytest.TESTDIR, META_FILENAME)
    with open(compare_metafile, "w") as f:
        pass

    result = _is_nonraw_object_directory(pytest.TESTDIR)
    assert(result is False)


    remove(pytest.TESTFILE)
    with open(compare_metafile, "w") as meta_file:
        metadata = {
            EXDIR_METANAME: {
                VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)

    result = _is_nonraw_object_directory(pytest.TESTDIR)
    assert(result is False)


    remove(pytest.TESTFILE)
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

    result = _is_nonraw_object_directory(pytest.TESTDIR)
    assert(result is False)

    remove(pytest.TESTFILE)
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

    result = _is_nonraw_object_directory(pytest.TESTDIR)
    assert(result is True)

    remove(pytest.TESTDIR)

    _create_object_directory(pytest.TESTDIR, DATASET_TYPENAME)
    result = _is_nonraw_object_directory(pytest.TESTDIR)
    assert(result is True)
