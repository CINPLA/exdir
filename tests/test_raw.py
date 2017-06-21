import os
import pytest
import pathlib
from exdir.core import Raw

def test_raw_init(setup_teardown_folder):
    raw = Raw(setup_teardown_folder[2], pathlib.PurePosixPath(""), "test_object", io_mode=None)

    assert raw.root_directory == setup_teardown_folder[2]
    assert raw.object_name == "test_object"
    assert raw.parent_path == pathlib.PurePosixPath("")
    assert raw.io_mode is None
    assert raw.relative_path == pathlib.PurePosixPath("test_object")
    assert raw.name == "/test_object"


def test_create_raw(setup_teardown_file):
    """Simple .create_raw call."""

    f = setup_teardown_file[3]
    raw = f.create_raw("test")

    raw2 = f["test"]

    assert raw == raw2

def test_require_raw(setup_teardown_file):
    """Raw is created if it doesn"t exist."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    raw = grp.require_group("foo")
    raw2 = grp.require_group("foo")

    raw3 = grp["foo"]

    assert raw == raw2
    assert raw == raw3
