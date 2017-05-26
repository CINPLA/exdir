import pytest
import os


from exdir.core import File, Group
from exdir.core import DATASET_TYPENAME, FILE_TYPENAME
from exdir.core import _create_object_directory, _is_nonraw_object_directory

from conftest import remove


def test_file_init(setup_teardown_folder):
    no_exdir = os.path.join(pytest.TESTPATH, "no_exdir")

    f = File(no_exdir, mode="w")
    f.close()
    assert _is_nonraw_object_directory(no_exdir + ".exdir")
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="w")
    f.close()
    assert _is_nonraw_object_directory(pytest.TESTFILE)
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="a")
    f.close()
    assert _is_nonraw_object_directory(pytest.TESTFILE)
    remove(pytest.TESTFILE)

    f = File(pytest.TESTFILE, mode="a")
    f.close()
    assert _is_nonraw_object_directory(pytest.TESTFILE)
    remove(pytest.TESTFILE)

    os.makedirs(pytest.TESTFILE)
    with pytest.raises(FileExistsError):
        f = File(pytest.TESTFILE, mode="w")

    remove(pytest.TESTFILE)

    _create_object_directory(pytest.TESTFILE, DATASET_TYPENAME)
    with pytest.raises(FileExistsError):
        f = File(pytest.TESTFILE, mode="w")

    remove(pytest.TESTFILE)

    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="r")
    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="r+")

    _create_object_directory(pytest.TESTFILE, FILE_TYPENAME)

    with pytest.raises(FileExistsError):
        f = File(pytest.TESTFILE, mode="w")

    remove(pytest.TESTFILE)

    _create_object_directory(pytest.TESTFILE, FILE_TYPENAME)
    f = File(pytest.TESTFILE, mode="w", allow_remove=True)
    remove(pytest.TESTFILE)

    _create_object_directory(pytest.TESTFILE, FILE_TYPENAME)

    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="w-")

    with pytest.raises(IOError):
        f = File(pytest.TESTFILE, mode="x")


def test_file_close(setup_teardown_folder):
    f = File(pytest.TESTFILE, mode="w")
    f.close()



def test_root_in(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file
    f.create_group("test")

    assert "/" in  f

def test_root_create(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file
    grp = f.create_group("/test")

    assert isinstance(grp, Group)

# TODO uncomment when enter and exit has been implemented
# # Feature: File objects can be used as context managers
# def test_context_manager(setup_teardown_folder):
#     """File objects can be used in with statements."""

#     no_exdir = os.path.join(pytest.TESTPATH, "no_exdir")

#     with File(no_exdir, mode="w") as f:
#         assert f

#     assert not f