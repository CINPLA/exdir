import os
import pathlib
import six
import yaml
import quantities as pq
import numpy as np
import pytest

import exdir
import exdir.core
import exdir.core.exdir_object as exob
import exdir.core.quantities_conversion as pqc
from exdir.core import filename_validation as fv

from conftest import remove


def test_convert_quantities():
    pq_value = pq.Quantity(1, "m")
    result = pqc.convert_quantities(pq_value)
    assert result == {"value": 1, "unit": "m"}

    pq_value = pq.Quantity([1, 2, 3], "m")
    result = pqc.convert_quantities(pq_value)
    assert result == {"value": [1, 2, 3], "unit": "m"}

    result = pqc.convert_quantities(np.array([1, 2, 3]))
    assert result == [1, 2, 3]

    result = pqc.convert_quantities(1)
    assert result == 1

    result = pqc.convert_quantities(2.3)
    assert result == 2.3

    pq_value = pq.UncertainQuantity([1, 2], "m", [3, 4])
    result = pqc.convert_quantities(pq_value)
    assert result == {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}

    pq_values = {"quantity": pq.Quantity(1, "m"),
                 "uq_quantity": pq.UncertainQuantity([1, 2], "m", [3, 4])}
    result = pqc.convert_quantities(pq_values)
    assert(result == {"quantity": {"unit": "m", "value": 1},
                      "uq_quantity": {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}})

    pq_values = {"list": [1, 2, 3], "quantity": pq.Quantity(1, "m")}
    pq_dict = {"list": [1, 2, 3], "quantity": {"unit": "m", "value": 1}}
    result = pqc.convert_quantities(pq_values)
    assert result == pq_dict


def test_convert_back_quantities():
    pq_dict = {"value": 1, "unit": "m"}
    result = pqc.convert_back_quantities(pq_dict)
    assert result == pq.Quantity(1, "m")

    pq_dict = {"value": [1, 2, 3], "unit": "m"}
    result = pqc.convert_back_quantities(pq_dict)
    assert np.array_equal(result, pq.Quantity([1, 2, 3], "m"))

    pq_dict = {"value": [1, 2, 3]}
    result = pqc.convert_back_quantities(pq_dict)
    assert result == pq_dict

    result = pqc.convert_back_quantities(1)
    assert result == 1

    result = pqc.convert_back_quantities(2.3)
    assert result == 2.3

    pq_dict = {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}
    result = pqc.convert_back_quantities(pq_dict)
    pq_value = pq.UncertainQuantity([1, 2], "m", [3, 4])

    assert isinstance(result, pq.UncertainQuantity)
    assert result.magnitude.tolist() == pq_value.magnitude.tolist()
    assert result.dimensionality.string == pq_value.dimensionality.string
    assert result.uncertainty.magnitude.tolist() == pq_value.uncertainty.magnitude.tolist()

    pq_dict = {"quantity": {"unit": "m", "value": 1},
               "uq_quantity": {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}}
    pq_values = {"quantity": pq.Quantity(1, "m"),
                 "uq_quantity": pq.UncertainQuantity([1, 2], "m", [3, 4])}
    result = pqc.convert_back_quantities(pq_values)
    assert result == pq_values

    pq_values = {"list": [1, 2, 3], "quantity": {"unit": "m", "value": 1}}
    result = pqc.convert_back_quantities(pq_values)
    assert result == {"list": [1, 2, 3], "quantity": pq.Quantity(1, "m")}


def test_assert_valid_name_simple(setup_teardown_folder):
    f = exdir.File(setup_teardown_folder[1], validate_name=fv.thorough)
    exob._assert_valid_name("abcdefghijklmnopqrstuvwxyz1234567890_-", f)
    with pytest.raises(NameError):
        exob._assert_valid_name("", f)

    exob._assert_valid_name("A", f)

    with pytest.raises(NameError):
        exob._assert_valid_name("\n", f)

    with pytest.raises(NameError):
        exob._assert_valid_name(six.unichr(0x4500), f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.META_FILENAME, f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.ATTRIBUTES_FILENAME, f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.RAW_FOLDER_NAME, f)


def test_assert_valid_name_none(setup_teardown_folder):
    f = exdir.File(setup_teardown_folder[1], validate_name=fv.minimal)
    valid_name = ("abcdefghijklmnopqrstuvwxyz1234567890_-")

    exob._assert_valid_name(valid_name, f)

    invalid_name = " "
    exob._assert_valid_name(invalid_name, f)

    invalid_name = "A"
    exob._assert_valid_name(invalid_name, f)

    invalid_name = "\n"
    exob._assert_valid_name(invalid_name, f)

    invalid_name = six.unichr(0x4500)
    exob._assert_valid_name(invalid_name, f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.META_FILENAME, f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.ATTRIBUTES_FILENAME, f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.RAW_FOLDER_NAME, f)


def test_create_object_directory(setup_teardown_folder):
    with pytest.raises(ValueError):
        exob._create_object_directory(pathlib.Path(setup_teardown_folder[2]), "wrong_typename")

    exob._create_object_directory(pathlib.Path(setup_teardown_folder[2]), exob.DATASET_TYPENAME)

    assert os.path.isdir(setup_teardown_folder[2])

    file_path = setup_teardown_folder[2] / exob.META_FILENAME
    assert os.path.isfile(file_path)

    compare_metadata = {
        exob.EXDIR_METANAME: {
            exob.TYPE_METANAME: exob.DATASET_TYPENAME,
            exob.VERSION_METANAME: 1}
    }

    with open(file_path, "r") as meta_file:
        metadata = yaml.safe_load(meta_file)

        assert metadata == compare_metadata

    with pytest.raises(IOError):
        exob._create_object_directory(pathlib.Path(setup_teardown_folder[2]), exob.DATASET_TYPENAME)


def test_is_nonraw_object_directory(setup_teardown_folder):
    os.makedirs(setup_teardown_folder[2])

    result = exob.is_nonraw_object_directory(setup_teardown_folder[2])
    assert result is False

    compare_metafile = setup_teardown_folder[2] / exob.META_FILENAME
    with open(compare_metafile, "w") as f:
        pass

    result = exob.is_nonraw_object_directory(setup_teardown_folder[2])
    assert result is False

    remove(setup_teardown_folder[1])
    with open(compare_metafile, "w") as meta_file:
        metadata = {
            exob.EXDIR_METANAME: {
                exob.VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)

    result = exob.is_nonraw_object_directory(setup_teardown_folder[2])
    assert result is False

    remove(setup_teardown_folder[1])
    with open(compare_metafile, "w") as meta_file:
        metadata = {
            exob.EXDIR_METANAME: {
                exob.TYPE_METANAME: "wrong_typename",
                exob.VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)

    result = exob.is_nonraw_object_directory(setup_teardown_folder[2])
    assert result is False

    remove(setup_teardown_folder[1])
    with open(compare_metafile, "w") as meta_file:
        metadata = {
            exob.EXDIR_METANAME: {
                exob.TYPE_METANAME: exob.DATASET_TYPENAME,
                exob.VERSION_METANAME: 1}
        }
        yaml.safe_dump(metadata,
                       meta_file,
                       default_flow_style=False,
                       allow_unicode=True)

    result = exob.is_nonraw_object_directory(setup_teardown_folder[2])
    assert result is True

    remove(setup_teardown_folder[2])

    exob._create_object_directory(pathlib.Path(setup_teardown_folder[2]), exob.DATASET_TYPENAME)
    result = exob.is_nonraw_object_directory(setup_teardown_folder[2])
    assert result is True


def test_root_directory(setup_teardown_file):
    f = setup_teardown_file[3]
    grp = f.create_group("foo")
    grp.create_group("bar")

    assert not exob.root_directory(setup_teardown_file[2])

    path = setup_teardown_file[1] / "foo" / "bar"
    assert pathlib.Path(setup_teardown_file[1]) == exob.root_directory(path)


def test_is_inside_exdir(setup_teardown_file):
    f = setup_teardown_file[3]

    grp = f.create_group("foo")
    grp.create_group("bar")

    path = setup_teardown_file[1] / "foo" / "bar"
    assert exob.is_inside_exdir(path)
    assert not exob.is_inside_exdir(setup_teardown_file[2])


def test_assert_inside_exdir(setup_teardown_file):
    f = setup_teardown_file[3]

    grp = f.create_group("foo")
    grp.create_group("bar")


    path = setup_teardown_file[1] / "foo" / "bar"
    assert exob.assert_inside_exdir(path) is None
    with pytest.raises(FileNotFoundError):
        exob.assert_inside_exdir(setup_teardown_file[2])


def test_open_object(setup_teardown_file):
    f = setup_teardown_file[3]

    grp = f.create_group("foo")
    grp2 = grp.create_group("bar")

    path = setup_teardown_file[1] / "foo" / "bar"
    loaded_grp = exob.open_object(path)

    assert grp2 == loaded_grp

    with pytest.raises(FileNotFoundError):
        exob.open_object(setup_teardown_file[2])
