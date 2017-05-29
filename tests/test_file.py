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

    with pytest.raises(ValueError):
        f = File(pytest.TESTFILE, mode="not existing")


def test_create(setup_teardown_folder):
    """Mode 'w' opens file in overwrite mode."""
    f = File(pytest.TESTFILE, 'w')
    assert f
    f.create_group('foo')
    f.close()

    f = File(pytest.TESTFILE, 'w', allow_remove=True)
    assert 'foo' not in f
    f.close()
    with pytest.raises(FileExistsError):
        f = File(pytest.TESTFILE, 'w')


def test_create_exclusive(setup_teardown_folder):
    """Mode 'w-' opens file in exclusive mode."""

    f = File(pytest.TESTFILE, 'w-')
    assert f
    f.close()
    with pytest.raises(IOError):
        File(pytest.TESTFILE, 'w-')

def test_append(setup_teardown_folder):
    """Mode 'a' opens file in append/readwrite mode, creating if necessary."""

    f = File(pytest.TESTFILE, 'a')
    assert f
    f.create_group('foo')
    assert 'foo' in f

    f = File(pytest.TESTFILE, 'a')
    assert 'foo' in f
    f.create_group('bar')
    assert 'bar' in f


def test_readonly(setup_teardown_folder):
    """Mode 'r' opens file in readonly mode."""

    f = File(pytest.TESTFILE, 'w')
    f.close()
    # TODO comment in when close is implemented
    # assert not f
    f = File(pytest.TESTFILE, 'r')
    assert f
    with pytest.raises(IOError):
        f.create_group('foo')
    f.close()

def test_readwrite(setup_teardown_folder):
    """Mode 'r+' opens existing file in readwrite mode."""

    f = File(pytest.TESTFILE, 'w')
    f.create_group('foo')
    f.close()
    f = File(pytest.TESTFILE, 'r+')
    assert 'foo' in f
    f.create_group('bar')
    assert 'bar' in f
    f.close()

def test_nonexistent_file(setup_teardown_folder):
    """Modes 'r' and 'r+' do not create files."""

    with pytest.raises(IOError):
        File(pytest.TESTFILE, 'r')
    with pytest.raises(IOError):
        File(pytest.TESTFILE, 'r+')

def test_invalid_mode(setup_teardown_folder):
    """Invalid modes raise ValueError."""
    with pytest.raises(ValueError):
        File(pytest.TESTFILE, 'Error mode')

def test_file_close(setup_teardown_folder):
    """Closing a file."""
    f = File(pytest.TESTFILE, mode="w")
    f.close()


def test_naming_rule_simple(setup_teardown_folder):
    """Test naming rule simple."""

    with pytest.raises(ValueError):
        File(pytest.TESTFILE, naming_rule='w')



def test_naming_rule_strict(setup_teardown_folder):
    """Test naming rule strict."""

    f = File(pytest.TESTFILE, naming_rule='strict')
    f.close()
    File(pytest.TESTFILE+"(" , naming_rule='strict')

    with pytest.raises(NameError):
        print(pytest.TESTFILE+"A")
        File(pytest.TESTFILE+"(" , naming_rule='strict')



def test_naming_rule_thorough(setup_teardown_folder):
    """Test naming rule thorough."""

    with pytest.raises(NotImplementedError):
        File(pytest.TESTFILE, naming_rule='thorough')



def test_naming_rule_none(setup_teardown_folder):
    """Test naming rule none."""

    with pytest.raises(ValueError):
        File(pytest.TESTFILE, naming_rule='')




def test_contains(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file
    f.create_group("test")

    assert "/" in  f
    assert "/test" in  f


def test_create_group(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file
    grp = f.create_group("/test")

    assert isinstance(grp, Group)

def test_require_group(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file

    grp = f.require_group("/foo")
    assert isinstance(grp, Group)


def test_open(setup_teardown_file):
    """Simple obj[name] opening."""
    f = setup_teardown_file
    grp = f.create_group("foo")

    grp2 = f["foo"]
    grp3 = f["/foo"]
    f = f["/"]

    assert grp == grp2
    assert grp2 == grp3
    assert f == f





# TODO uncomment when enter and exit has been implemented
# # Feature: File objects can be used as context managers
# def test_context_manager(setup_teardown_folder):
#     """File objects can be used in with statements."""

#     no_exdir = os.path.join(pytest.TESTPATH, "no_exdir")

#     with File(no_exdir, mode="w") as f:
#         assert f

#     assert not f