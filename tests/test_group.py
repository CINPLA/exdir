# -*- coding: utf-8 -*-
#
# This file is part of Exdir, the Experimental Directory Structure.
#
# Copyright 2017 Simen Tennøe, Svenn-Arne Dragly
#
# License: MIT, see "LICENSE" file for the full license terms.
#
# This file contains code from h5py, a Python interface to the HDF5 library,
# licensed under a standard 3-clause BSD license
# with copyright Andrew Collette and contributors.
# See http://www.h5py.org and the "3rdparty/h5py-LICENSE" file for details.


import os
import pytest
try:
    import pathlib
except ImportError as e:
    try:
        import pathlib2 as pathlib
    except ImportError:
        raise e
import numpy as np
try:
    from collections.abc import KeysView, ValuesView, ItemsView
except:
    from collections import KeysView, ValuesView, ItemsView

from exdir.core import Group, File, Dataset
from exdir import validation as fv
from conftest import remove

# tests for Group class
def test_group_init(setup_teardown_folder):
    group = Group(setup_teardown_folder[2], pathlib.PurePosixPath(""), "test_object", file=None)

    assert group.root_directory == setup_teardown_folder[2]
    assert group.object_name == "test_object"
    assert group.parent_path == pathlib.PurePosixPath("")
    assert group.file is None
    assert group.relative_path == pathlib.PurePosixPath("test_object")
    assert group.name == "/test_object"


# New groups can be created via .create_group method

def test_create_group(setup_teardown_file):
    """Simple .create_group call."""

    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.create_group("a")

    assert isinstance(grp2, Group)

    grp3 = grp.create_group("b/")
    assert isinstance(grp3, Group)


def test_len(setup_teardown_file):
    """Simple .create_group call."""

    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.create_group("a")

    grp3 = grp.create_group("b")

    assert len(grp) == 2
    assert len(grp2) == 0
    assert len(grp3) == 0


def test_get(setup_teardown_file):
    """Simple .create_group call."""

    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.create_group("a")

    grp2_get = grp.get('a')

    grp3_get = grp.get('b')

    assert grp2 == grp2_get
    assert grp3_get is None


def test_create_group_absolute(setup_teardown_file):
    """Starting .create_group argument with /."""

    f = setup_teardown_file[3]
    grp = f.create_group("/a")

    with pytest.raises(NotImplementedError):
        grp.create_group("/b")


def test_create_existing_twice(exdir_tmpfile):
    exdir_tmpfile.create_group("test")
    with pytest.raises(RuntimeError):
        exdir_tmpfile.create_group("test")


def test_create_intermediate(setup_teardown_file):
    """intermediate groups can be created automatically."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.create_group("foo/bar/baz")

    assert isinstance(grp["foo/bar/baz"], Group)
    assert isinstance(grp2, Group)

    assert grp2.name == "/test/foo/bar/baz"
    assert "foo" in grp
    assert "bar" in grp.require_group("foo")
    assert "baz" in grp.require_group("foo").require_group("bar")
    assert grp.require_group("foo").require_group("bar").require_group("baz") == grp2


def test_create_exception(setup_teardown_file):
    """Name conflict causes group creation to fail with IOError."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp.create_group("foo")

    with pytest.raises(RuntimeError):
        grp.create_group("foo")
        grp.create_group("foo/")


# Feature: Groups can be auto-created, or opened via .require_group
def test_open_existing(setup_teardown_file):
    """Existing group is opened and returned."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.create_group("foo")
    grp3 = grp.require_group("foo")
    grp4 = grp.require_group("foo/")

    assert grp2 == grp3
    assert grp2.name == grp4.name
    assert grp2 == grp4


def test_create(setup_teardown_file):
    """Group is created if it doesn"t exist."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.require_group("foo")
    assert isinstance(grp2, Group)
    assert grp2.name == "/test/foo"


def test_require_exception(setup_teardown_file):
    """Opening conflicting object results in TypeError."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp.create_dataset("foo", (1,))

    with pytest.raises(TypeError):
        grp.require_group("foo")


def test_set_item_intermediate(exdir_tmpfile):
    group1 = exdir_tmpfile.create_group("group1")
    group2 = group1.create_group("group2")
    group3 = group2.create_group("group3")
    exdir_tmpfile["group1/group2/group3/dataset"] = np.array([1, 2, 3])

    assert np.array_equal(exdir_tmpfile["group1/group2/group3/dataset"].data, np.array([1, 2, 3]))


# Feature: Objects can be unlinked via "del" operator
def test_delete_group(setup_teardown_file):
    """Object deletion via "del"."""

    f = setup_teardown_file[3]
    grp = f.create_group("test")
    grp.create_group("foo")

    assert "foo" in grp
    del grp["foo"]
    assert "foo" not in grp


def test_delete_group_from_file(setup_teardown_file):
    """Object deletion via "del"."""

    f = setup_teardown_file[3]
    grp = f.create_group("test")

    assert "test" in f
    del f["test"]
    assert "test" not in f


def test_delete_raw(setup_teardown_file):
    """Object deletion via "del"."""

    f = setup_teardown_file[3]
    grp = f.create_group("test")
    grp.create_raw("foo")

    assert "foo" in grp
    del grp["foo"]
    assert "foo" not in grp


def test_nonexisting(setup_teardown_file):
    """Deleting non-existent object raises KeyError."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    mtch = "No such object: 'foo' in path *"
    with pytest.raises(KeyError, match=mtch):
        del grp["foo"]


def test_readonly_delete_exception(setup_teardown_file):
    """Deleting object in readonly file raises KeyError."""
    f = setup_teardown_file[3]
    f.close()

    f = File(setup_teardown_file[1], "r")
    mtch = "Cannot change data on file in read only 'r' mode"
    with pytest.raises(IOError, match=mtch):
        del f["foo"]


def test_delete_dataset(setup_teardown_file):
    """Create new dataset with no conflicts."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    foo = grp.create_dataset('foo', (10, 3), 'f')
    assert isinstance(grp['foo'], Dataset)
    assert foo.shape == (10, 3)
    bar = grp.require_dataset('bar', data=(3, 10))
    del foo
    assert 'foo' in grp
    del grp['foo']
    mtch = "No such object: 'foo' in path *"
    with pytest.raises(KeyError, match=mtch):
        grp['foo']
    # the "bar" dataset is intact
    assert isinstance(grp['bar'], Dataset)
    assert np.all(bar[:] == (3, 10))
    # even though the dataset is deleted on file, the memmap stays open until
    # garbage collected
    del grp['bar']
    assert bar.shape == (2,)
    assert np.all(bar[:] == (3, 10))
    with pytest.raises(KeyError):
        grp['bar']

# Feature: Objects can be opened via indexing syntax obj[name]

def test_open(setup_teardown_file):
    """Simple obj[name] opening."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    grp2 = grp.create_group("foo")

    grp3 = grp["foo"]
    grp4 = grp["foo/"]

    assert grp2 == grp3
    assert grp2.name == grp4.name
    assert grp2 == grp4

    with pytest.raises(NotImplementedError):
        grp["/test"]


def test_open_deep(setup_teardown_file):
    """Simple obj[name] opening."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")
    grp2 = grp.create_group("a")
    grp3 = grp2.create_group("b")

    grp4 = grp["a/b"]

    assert grp3 == grp4


def test_nonexistent(setup_teardown_file):
    """Opening missing objects raises KeyError."""
    f = setup_teardown_file[3]
    mtch = "No such object: 'foo' in path *"
    with pytest.raises(KeyError, match=mtch):
        f["foo"]


# Feature: The Python "in" builtin tests for containership
def test_contains(setup_teardown_file):
    """'in' builtin works for containership."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp.create_group("b")

    assert "b" in grp
    assert not "c" in grp

    with pytest.raises(NotImplementedError):
        assert "/b" in grp


def test_contains_deep(setup_teardown_file):
    """'in' builtin works for containership."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.create_group("a")
    grp3 = grp2.create_group("b")

    assert "a/b" in grp


def test_empty(setup_teardown_file):
    """Empty strings work properly and aren"t contained."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    assert "" not in grp

def test_dot(setup_teardown_file):
    """Current group "." is always contained."""
    f = setup_teardown_file[3]

    assert "." in f

def test_root(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    with pytest.raises(NotImplementedError):
        assert "/" in grp

def test_trailing_slash(setup_teardown_file):
    """Trailing slashes are unconditionally ignored."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp.create_group("a")
    assert "a/" in grp
    assert "a//" in grp
    assert "a////" in grp

# Feature: Standard Python 3 .keys, .values, etc. methods are available
def test_keys(setup_teardown_file):
    """.keys provides a key view."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp.create_group("a")
    grp.create_group("b")
    grp.create_group("c")
    grp.create_group("d")

    assert isinstance(grp.keys(), KeysView)
    assert sorted(list(grp.keys())) == ["a", "b", "c", "d"]

def test_values(setup_teardown_file):
    """.values provides a value view."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grpa = grp.create_group("a")
    grpb = grp.create_group("b")
    grpc = grp.create_group("c")
    grpd = grp.create_group("d")

    assert isinstance(grp.values(), ValuesView)
    assert list(grp.values()) == [grpa, grpb, grpc, grpd]

def test_items(setup_teardown_file):
    """.items provides an item view."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grpa = grp.create_group("a")
    grpb = grp.create_group("b")
    grpc = grp.create_group("c")
    grpd = grp.create_group("d")

    groups = [grpa, grpb, grpc, grpd]
    names = ["a", "b", "c", "d"]

    assert isinstance(grp.items(), ItemsView)

    for i, (key, value) in enumerate(grp.items()):
        assert key == names[i]
        assert value == groups[i]




# Feature: You can iterate over group members via "for x in y", etc.

def test_iter(setup_teardown_file):
    """'for x in y' iteration."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp.create_group("a")
    grp.create_group("b")
    grp.create_group("c")
    grp.create_group("d")

    lst = [x for x in grp]
    assert lst == ["a", "b", "c", "d"]

def test_iter_zero(setup_teardown_file):
    """Iteration works properly for the case with no group members."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    lst = [x for x in grp]
    assert lst == []


# Feature: Equal

def test_eq(setup_teardown_file):
    """Test equal."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.create_group("a")

    assert grp2 == grp2
    assert grp != grp2


# Feature: Parent
def test_eq_parent(setup_teardown_file):
    """Test equal."""
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    grp2 = grp.create_group("a")

    grp_parent = grp2.parent

    assert grp == grp_parent


# Feature: Test different naming rules
def test_validate_name_simple(setup_teardown_folder):
    """Test naming rule simple."""
    f = File(setup_teardown_folder[1], name_validation=fv.thorough)
    grp = f.create_group("test")

    grp.create_group("abcdefghijklmnopqrstuvwxyz1234567890_-")

    with pytest.raises(NameError):
        grp.create_group("()")

    f.close()
    remove(setup_teardown_folder[1])

    f = File(setup_teardown_folder[1], name_validation=fv.thorough)
    grp = f.create_group("test")
    grp.create_group("aa")

    with pytest.raises(RuntimeError):
        grp.create_group("AA")


def test_validate_name_strict(setup_teardown_folder):
    """Test naming rule strict."""
    f = File(setup_teardown_folder[1], name_validation=fv.strict)
    f.create_group("abcdefghijklmnopqrstuvwxyz1234567890_-")

    with pytest.raises(NameError):
        f.create_group("A")

    f.close()


def test_validate_name_none(setup_teardown_folder):
    """Test naming rule with error."""
    f = File(setup_teardown_folder[1], name_validation=fv.none)
    f.create_group("abcdefghijklmnopqrstuvwxyz1234567890_-")
    f.create_group("ABNCUIY&z()(d()&")

    f.close()
