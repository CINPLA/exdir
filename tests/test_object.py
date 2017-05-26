import pytest
import os
import yaml

from exdir.core import Object, Attribute
from exdir.core import DATASET_TYPENAME, GROUP_TYPENAME, ATTRIBUTES_FILENAME, META_FILENAME
from exdir.core import _create_object_directory, _is_nonraw_object_directory


# tests for Object class

def test_object_init(setup_teardown_folder):
    obj = Object(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert obj.root_directory == pytest.TESTDIR
    assert obj.object_name == "test_object"
    assert obj.parent_path == ""
    assert obj.io_mode is None
    assert obj.relative_path == os.path.join("", "test_object")
    assert obj.name == os.sep + os.path.join("", "test_object")


def test_object_attrs(setup_teardown_folder):
    obj = Object(pytest.TESTDIR, "", "test_object", io_mode=None)

    _create_object_directory(pytest.TESTDIR, DATASET_TYPENAME)
    _create_object_directory(os.path.join(pytest.TESTDIR, "test_object"),
                             GROUP_TYPENAME)

    assert isinstance(obj.attrs, Attribute)
    assert obj.attrs.mode.value == 1
    obj.attrs = "test value"

    assert _is_nonraw_object_directory(os.path.join(pytest.TESTDIR, "test_object"))

    with open(os.path.join(pytest.TESTDIR, "test_object", ATTRIBUTES_FILENAME), "r") as meta_file:
        meta_data = yaml.safe_load(meta_file)

        assert meta_data == "test value"


def test_object_meta(setup_teardown_folder):
    obj = Object(pytest.TESTDIR, "", "test_object", io_mode=None)

    _create_object_directory(pytest.TESTDIR, DATASET_TYPENAME)
    _create_object_directory(os.path.join(pytest.TESTDIR, "test_object"),
                             GROUP_TYPENAME)

    assert isinstance(obj.meta, Attribute)
    assert obj.meta.mode.value == 2
    with pytest.raises(AttributeError):
        obj.meta = "test value"


def test_object_directory(setup_teardown_folder):
    obj = Object(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert obj.directory == os.path.join(pytest.TESTDIR, "", "test_object")


def test_object_attributes_filename(setup_teardown_folder):
    obj = Object(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert obj.attributes_filename == os.path.join(pytest.TESTDIR, "", "test_object", ATTRIBUTES_FILENAME)


def test_object_meta_filename(setup_teardown_folder):
    obj = Object(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert obj.meta_filename == os.path.join(pytest.TESTDIR, "", "test_object", META_FILENAME)


def test_object_create_raw(setup_teardown_folder):
    obj = Object(pytest.TESTDIR, "", "test_object", io_mode=None)

    _create_object_directory(pytest.TESTDIR, DATASET_TYPENAME)
    _create_object_directory(os.path.join(pytest.TESTDIR, "test_object"),
                             GROUP_TYPENAME)

    obj.create_raw("test_raw")
    assert os.path.isdir(os.path.join(pytest.TESTDIR, "test_object", "test_raw"))

    with pytest.raises(IOError):
        obj.create_raw("test_raw")


def test_object_require_raw(setup_teardown_folder):
    obj = Object(pytest.TESTDIR, "", "test_object", io_mode=None)

    _create_object_directory(pytest.TESTDIR, DATASET_TYPENAME)
    _create_object_directory(os.path.join(pytest.TESTDIR, "test_object"),
                             GROUP_TYPENAME)

    obj.require_raw("test_raw")
    assert os.path.isdir(os.path.join(pytest.TESTDIR, "test_object", "test_raw"))

    obj.require_raw("test_raw")
    assert os.path.isdir(os.path.join(pytest.TESTDIR, "test_object", "test_raw"))
