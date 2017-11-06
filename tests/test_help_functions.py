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
from exdir.core import filename_validation as fv

from conftest import remove


def test_assert_valid_name_minimal(setup_teardown_folder):
    f = exdir.File(setup_teardown_folder[1], validate_name=fv.minimal)
    exob._assert_valid_name("abcdefghijklmnopqrstuvwxyz1234567890_-", f)
    with pytest.raises(NameError):
        exob._assert_valid_name("", f)

    exob._assert_valid_name("A", f)

    exob._assert_valid_name("\n", f)

    exob._assert_valid_name(six.unichr(0x4500), f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.META_FILENAME, f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.ATTRIBUTES_FILENAME, f)

    with pytest.raises(NameError):
        exob._assert_valid_name(exob.RAW_FOLDER_NAME, f)


def test_assert_valid_name_thorough(setup_teardown_folder):
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
    f = exdir.File(setup_teardown_folder[1], validate_name=fv.none)
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

    exob._assert_valid_name(exob.META_FILENAME, f)

    exob._assert_valid_name(exob.ATTRIBUTES_FILENAME, f)

    exob._assert_valid_name(exob.RAW_FOLDER_NAME, f)


def test_create_object_directory(setup_teardown_folder):
    with pytest.raises(ValueError):
        exob._create_object_directory(pathlib.Path(setup_teardown_folder[2]), "wrong_typename")

    exob._create_object_directory(pathlib.Path(setup_teardown_folder[2]), exob.DATASET_TYPENAME)

    assert setup_teardown_folder[2].is_dir()

    file_path = setup_teardown_folder[2] / exob.META_FILENAME
    assert file_path.is_file()

    compare_metadata = {
        exob.EXDIR_METANAME: {
            exob.TYPE_METANAME: exob.DATASET_TYPENAME,
            exob.VERSION_METANAME: 1}
    }

    with file_path.open("r", encoding="utf-8") as meta_file:
        metadata = yaml.safe_load(meta_file)

        assert metadata == compare_metadata

    with pytest.raises(IOError):
        exob._create_object_directory(pathlib.Path(setup_teardown_folder[2]), exob.DATASET_TYPENAME)


def test_is_nonraw_object_directory(setup_teardown_folder):
    setup_teardown_folder[2].mkdir()

    result = exob.is_nonraw_object_directory(setup_teardown_folder[2])
    assert result is False

    compare_metafile = setup_teardown_folder[2] / exob.META_FILENAME
    with compare_metafile.open("w", encoding="utf-8") as f:
        pass

    result = exob.is_nonraw_object_directory(setup_teardown_folder[2])
    assert result is False

    remove(setup_teardown_folder[1])
    with compare_metafile.open("w", encoding="utf-8") as meta_file:
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
    with compare_metafile.open("w", encoding="utf-8") as meta_file:
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
    with compare_metafile.open("w", encoding="utf-8") as meta_file:
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
