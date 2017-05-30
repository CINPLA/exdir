import os
import pytest
from exdir.core import Raw

def test_raw_init(setup_teardown_folder):
    raw = Raw(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert raw.root_directory == pytest.TESTDIR
    assert raw.object_name == "test_object"
    assert raw.parent_path == ""
    assert raw.io_mode is None
    assert raw.relative_path == os.path.join("", "test_object")
    assert raw.name == "/" + os.path.join("", "test_object")


def test_create_raw(setup_teardown_file):
    """Simple .create_raw call."""

    f = setup_teardown_file
    raw = f.create_raw("test")

    raw2 = f["test"]

    assert raw == raw2