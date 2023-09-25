# -*- coding: utf-8 -*-
#
# This file is part of Exdir, the Experimental Directory Structure.
#
# Copyright 2017 Simen Tennøe
#
# License: MIT, see "LICENSE" file for the full license terms.
#
# This file contains code from h5py, a Python interface to the HDF5 library,
# licensed under a standard 3-clause BSD license
# with copyright Andrew Collette and contributors.
# See http://www.h5py.org and the "3rdparty/h5py-LICENSE" file for details.


import pytest
import os
try:
    import pathlib
except ImportError as e:
    try:
        import pathlib2 as pathlib
    except ImportError:
        raise e

from exdir.core import File, Group
from exdir.core.exdir_object import _create_object_directory, is_nonraw_object_directory, DATASET_TYPENAME, FILE_TYPENAME
import exdir.core.exdir_object as exob
from exdir import validation as fv

import numpy as np

from conftest import remove


def test_file_init(setup_teardown_folder):
    no_exdir = setup_teardown_folder[0] / "no_exdir"

    f = File(no_exdir, mode="w")
    f.close()
    assert is_nonraw_object_directory(no_exdir.with_suffix(".exdir"))
    remove(setup_teardown_folder[1])

    f = File(setup_teardown_folder[1], mode="w")
    f.close()
    assert is_nonraw_object_directory(setup_teardown_folder[1])
    remove(setup_teardown_folder[1])

    f = File(setup_teardown_folder[1], mode="a")
    f.close()
    assert is_nonraw_object_directory(setup_teardown_folder[1])
    remove(setup_teardown_folder[1])

    f = File(setup_teardown_folder[1], mode="a")
    f.close()
    assert is_nonraw_object_directory(setup_teardown_folder[1])
    remove(setup_teardown_folder[1])

    setup_teardown_folder[1].mkdir(parents=True)
    with pytest.raises(RuntimeError):
        f = File(setup_teardown_folder[1], mode="w")

    remove(setup_teardown_folder[1])

    _create_object_directory(pathlib.Path(setup_teardown_folder[1]), exob._default_metadata(DATASET_TYPENAME))
    with pytest.raises(RuntimeError):
        f = File(setup_teardown_folder[1], mode="w")

    remove(setup_teardown_folder[1])

    with pytest.raises(RuntimeError):
        f = File(setup_teardown_folder[1], mode="r")
    with pytest.raises(RuntimeError):
        f = File(setup_teardown_folder[1], mode="r+")

    _create_object_directory(pathlib.Path(setup_teardown_folder[1]), exob._default_metadata(FILE_TYPENAME))

    with pytest.raises(RuntimeError):
        f = File(setup_teardown_folder[1], mode="w")

    remove(setup_teardown_folder[1])

    _create_object_directory(pathlib.Path(setup_teardown_folder[1]), exob._default_metadata(FILE_TYPENAME))
    f = File(setup_teardown_folder[1], mode="w", allow_remove=True)
    remove(setup_teardown_folder[1])

    _create_object_directory(pathlib.Path(setup_teardown_folder[1]), exob._default_metadata(FILE_TYPENAME))

    with pytest.raises(RuntimeError):
        f = File(setup_teardown_folder[1], mode="w-")

    with pytest.raises(RuntimeError):
        f = File(setup_teardown_folder[1], mode="x")

    with pytest.raises(ValueError):
        f = File(setup_teardown_folder[1], mode="not existing")


def test_create(setup_teardown_folder):
    """Mode 'w' opens file in overwrite mode."""
    f = File(setup_teardown_folder[1], 'w')
    assert isinstance(f, File)
    f.create_group('foo')
    f.close()

    f = File(setup_teardown_folder[1], 'w', allow_remove=True)
    assert 'foo' not in f
    f.close()
    with pytest.raises(RuntimeError):
        f = File(setup_teardown_folder[1], 'w')


def test_create_exclusive(setup_teardown_folder):
    """Mode 'w-' opens file in exclusive mode."""

    f = File(setup_teardown_folder[1], 'w-')
    assert isinstance(f, File)
    f.close()
    with pytest.raises(RuntimeError):
        File(setup_teardown_folder[1], 'w-')


def test_append(setup_teardown_folder):
    """Mode 'a' opens file in append/readwrite mode, creating if necessary."""

    f = File(setup_teardown_folder[1], 'a')
    assert isinstance(f, File)
    f.create_group('foo')
    assert 'foo' in f

    f = File(setup_teardown_folder[1], 'a')
    assert 'foo' in f
    f.create_group('bar')
    assert 'bar' in f


def test_readonly(setup_teardown_folder):
    """Mode 'r' opens file in readonly mode."""

    f = File(setup_teardown_folder[1], 'w')
    f.close()
    assert not f
    f = File(setup_teardown_folder[1], 'r')
    assert isinstance(f, File)
    with pytest.raises(IOError):
        f.create_group('foo')
        f.create_dataset("bar", (2))
    f.close()


def test_readwrite(setup_teardown_folder):
    """Mode 'r+' opens existing file in readwrite mode."""

    f = File(setup_teardown_folder[1], 'w')
    f.create_group('foo')
    f.close()
    f = File(setup_teardown_folder[1], 'r+')
    assert 'foo' in f
    f.create_group('bar')
    assert 'bar' in f
    f.close()


def test_nonexistent_file(setup_teardown_folder):
    """Modes 'r' and 'r+' do not create files."""

    with pytest.raises(RuntimeError):
        File(setup_teardown_folder[1], 'r')
    with pytest.raises(RuntimeError):
        File(setup_teardown_folder[1], 'r+')


def test_invalid_mode(setup_teardown_folder):
    """Invalid modes raise ValueError."""
    with pytest.raises(ValueError):
        File(setup_teardown_folder[1], 'Error mode')


def test_file_close(setup_teardown_folder):
    """Closing a file."""
    f = File(setup_teardown_folder[1], mode="w")
    f.close()


def test_validate_name_thorough(setup_teardown_folder):
    """Test naming rule thorough."""
    f = File(setup_teardown_folder[0] / "test.exdir", name_validation=fv.thorough)
    f.close()

    with pytest.raises(RuntimeError):
        File(setup_teardown_folder[0] / "Test.exdir", name_validation=fv.thorough)
    with pytest.raises(NameError):
        File(setup_teardown_folder[0] / "tes#.exdir", name_validation=fv.thorough)


def test_validate_name_strict(setup_teardown_folder):
    """Test naming rule strict."""
    f = File(setup_teardown_folder[1], name_validation=fv.strict)
    f.close()

    with pytest.raises(NameError):
        File(setup_teardown_folder[1].with_suffix(".exdirA"), name_validation=fv.strict)


def test_validate_name_error(setup_teardown_folder):
    """Test naming rule with error."""

    with pytest.raises(ValueError):
        File(setup_teardown_folder[1], name_validation='Error rule')


def test_validate_name_none(setup_teardown_folder):
    """Test naming rule with error."""

    File(setup_teardown_folder[1].with_name("test&().exdir"), name_validation=fv.none)


def test_opening_with_different_validate_name(setup_teardown_folder):
    """Test opening with wrong naming rule."""

    f = File(setup_teardown_folder[1], "w", name_validation=fv.none)
    f.create_group("AAA")
    f.close()

    # TODO changing name validation should result in warning/error
    f = File(setup_teardown_folder[1], "a", name_validation=fv.thorough)
    with pytest.raises(RuntimeError):
        f.create_group("aaa")
    f.close()


def test_contains(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file[3]
    f.create_group("test")

    assert "/" in f
    assert "/test" in f


def test_create_group(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file[3]
    grp = f.create_group("/test")

    assert isinstance(grp, Group)


def test_require_group(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file[3]

    grp = f.require_group("/foo")
    assert isinstance(grp, Group)


def test_open(setup_teardown_file):
    """thorough obj[name] opening."""
    f = setup_teardown_file[3]
    grp = f.create_group("foo")

    grp2 = f["foo"]
    grp3 = f["/foo"]
    f = f["/"]

    assert grp == grp2
    assert grp2 == grp3
    assert f == f


def test_open_mode(setup_teardown_folder):
    # must exist
    for mode in ["r+", "r"]:
        with pytest.raises(RuntimeError):
            f = File(setup_teardown_folder[1], mode)
    # create if not exist
    for mode in ["a", "w", "w-"]:
        remove(setup_teardown_folder[1])
        f = File(setup_teardown_folder[1], mode)
        f.require_dataset('dset', np.arange(10))
        f.attrs['can_overwrite'] = 42
        f.attrs['can_overwrite'] = 14
        f.require_group('mygroup')

    remove(setup_teardown_folder[1])
    f = File(setup_teardown_folder[1], 'w')
    f.close()  # dummy close
    # read write if exist
    f = File(setup_teardown_folder[1], "r+")
    f.require_group('mygroup')
    f.require_dataset('dset', np.arange(10))
    f.attrs['can_overwrite'] = 42
    f.attrs['can_overwrite'] = 14

    # read only, can not write
    f = File(setup_teardown_folder[1], 'r')
    with pytest.raises(IOError):
        f.require_dataset('dset', np.arange(10))
        f.attrs['can_not_write'] = 42
        f.create_group('mygroup')


def test_open_two_attrs(setup_teardown_file):
    f = setup_teardown_file[3]

    f.attrs['can_overwrite'] = 42
    f.attrs['another_attribute'] = 14


def test_exc(setup_teardown_file):
    """'in' on closed group returns False."""
    f = setup_teardown_file[3]

    f.create_group("a")
    f.close()

    assert not f
    assert "a" not in f


def test_close_group(setup_teardown_file):
    """'closed file is unable to handle."""
    f = setup_teardown_file[3]

    grp = f.create_group("group")

    f.close()
    assert not f
    assert "group" not in f
    assert 'dataset' not in f

    # unable to create new stuff
    mtch = "Unable to operate on closed File instance."
    with pytest.raises(IOError, match=mtch):
        f.create_group("group")
    with pytest.raises(IOError, match=mtch):
        grp.create_group("group")
    with pytest.raises(IOError, match=mtch):
        grp.attrs = {'group': 'attrs'}


def test_close_attrs(setup_teardown_file):
    """'closed file is unable to handle."""
    f = setup_teardown_file[3]

    grp = f.create_group("group")
    dset = f.create_dataset('dataset', data=np.array([1,2,3]))
    raw = f.create_raw('raw')
    f.attrs = {'file': 'attrs'}
    file_attrs = f.attrs
    f.close()

    mtch = "Unable to operate on closed File instance."
    with pytest.raises(IOError, match=mtch):
        f.attrs = {'file': 'attrs'}
    with pytest.raises(IOError, match=mtch):
        file_attrs['new'] = 'yo'

    # unable to retrieve stuff
    with pytest.raises(IOError, match=mtch):
        file_attrs['file']
    with pytest.raises(IOError, match=mtch):
        f.attrs
    assert 'file' not in file_attrs


def test_close_raw(setup_teardown_file):
    """'closed file is unable to handle."""
    f = setup_teardown_file[3]

    raw = f.create_raw('raw')
    f.close()

    assert "raw" not in f

    # unable to create new stuff
    mtch = "Unable to operate on closed File instance."
    with pytest.raises(IOError, match=mtch):
        f.create_raw('raw')

    # unable to retrieve
    with pytest.raises(IOError, match=mtch):
        f['raw']


def test_close_dataset(setup_teardown_file):
    """'closed file is unable to handle."""
    f = setup_teardown_file[3]

    grp = f.create_group("group")
    dset = f.create_dataset('dataset', data=np.array([1,2,3]))
    dset.attrs = {'dataset': 'attrs'}
    dset_attrs = dset.attrs
    data = dset.data
    f.close()

    assert 'dataset' not in f

    # unable to create new stuff
    mtch = "Unable to operate on closed File instance."

    with pytest.raises(IOError, match=mtch):
        f.create_dataset('dataset', data=np.array([1,2,3]))
    with pytest.raises(IOError, match=mtch):
        grp.create_dataset('dataset', data=np.array([1,2,3]))
    with pytest.raises(IOError, match=mtch):
        dset.attrs = {'dataset': 'attrs'}
    with pytest.raises(IOError, match=mtch):
        dset_attrs['new'] = 'yo'

    # unable to retrieve stuff
    with pytest.raises(IOError, match=mtch):
        dset.data
    with pytest.raises(IOError, match=mtch):
        dset.shape
    with pytest.raises(IOError, match=mtch):
        dset.dtype
    with pytest.raises(IOError, match=mtch):
        dset.attrs

    assert 'dataset' not in dset_attrs

    # TODO unable to close datasets: uncomment when done
    # assert 1 not in data
    # data[:] = np.array([3,2,1]) # TODO should give error
    # f.io_mode = 1
    # assert np.array_equal(dset.data, np.array([1,2,3]))


# Feature: File objects can be used as context managers
def test_context_manager(setup_teardown_folder):
    """File objects can be used in with statements."""

    no_exdir = setup_teardown_folder[2]

    with File(no_exdir, mode="w") as f:
        assert isinstance(f, File)

    assert not f
