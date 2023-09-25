import os
import pytest
try:
    import pathlib
except ImportError as e:
    try:
        import pathlib2 as pathlib
    except ImportError:
        raise e
from exdir.core import Raw

def test_raw_init(setup_teardown_folder):
    raw = Raw(setup_teardown_folder[2], pathlib.PurePosixPath(""), "test_object", file=None)

    assert raw.root_directory == setup_teardown_folder[2]
    assert raw.object_name == "test_object"
    assert raw.parent_path == pathlib.PurePosixPath("")
    assert raw.file is None
    assert raw.relative_path == pathlib.PurePosixPath("test_object")
    assert raw.name == "/test_object"


def test_create_raw(setup_teardown_file):
    """Simple .create_raw call."""

    f = setup_teardown_file[3]
    raw = f.create_raw("test")

    raw2 = f["test"]

    assert (f.root_directory / "test").exists()

    assert raw == raw2


def test_require_raw(setup_teardown_file):
    """Raw is created if it doesn't exist."""

    f = setup_teardown_file[3]
    grp = f.create_group("test")

    raw = grp.require_raw("foo")
    raw2 = grp.require_raw("foo")

    raw3 = grp["foo"]

    assert (f.root_directory / "test" / "foo").exists()

    assert raw == raw2
    assert raw == raw3


def test_create_raw_twice(exdir_tmpfile):
    exdir_tmpfile.create_raw("test")
    with pytest.raises(RuntimeError):
        exdir_tmpfile.create_raw("test")


def test_create_dataset_raw(exdir_tmpfile):
    group = exdir_tmpfile.create_group("group")
    dataset = group.create_dataset("dataset", shape=(1, 1), dtype='float32')
    raw = dataset.create_raw("raw")
    assert (exdir_tmpfile.directory / "group" / "dataset" / "raw").exists()
