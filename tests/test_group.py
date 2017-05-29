import os
import pytest
from collections.abc import KeysView, ValuesView, ItemsView

from exdir.core import Group, File

# tests for Group class
def test_group_init(setup_teardown_folder):
    group = Group(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert group.root_directory == pytest.TESTDIR
    assert group.object_name == "test_object"
    assert group.parent_path == ""
    assert group.io_mode is None
    assert group.relative_path == os.path.join("", "test_object")
    assert group.name == "/" + os.path.join("", "test_object")


# New groups can be created via .create_group method

def test_create_group(setup_teardown_file):
    """Simple .create_group call."""

    f = setup_teardown_file
    grp = f.create_group("test")

    grp2 = grp.create_group("a")

    assert isinstance(grp2, Group)

    grp3 = grp.create_group("b/")
    assert isinstance(grp3, Group)


def test_create_group_absolute(setup_teardown_file):
    """Starting .create_group argument with /."""

    f = setup_teardown_file
    grp = f.create_group("/a")

    with pytest.raises(NotImplementedError):
        grp.create_group("/b")


# TODO update this test when it is implemented
def test_create_intermediate(setup_teardown_file):
    """Intermediate groups can be created automatically."""
    f = setup_teardown_file
    grp = f.create_group("test")

    with pytest.raises(NotImplementedError):
        grp.create_group("foo/bar/baz")

    # assert grp.name == "/foo/bar/baz"


def test_create_exception(setup_teardown_file):
    """Name conflict causes group creation to fail with IOError."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp.create_group("foo")

    with pytest.raises(NameError):
        grp.create_group("foo")
        grp.create_group("foo/")


# Feature: Groups can be auto-created, or opened via .require_group
def test_open_existing(setup_teardown_file):
    """Existing group is opened and returned."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp2 = grp.create_group("foo")
    grp3 = grp.require_group("foo")
    grp4 = grp.require_group("foo/")

    assert grp2 == grp3
    assert grp2 == grp4


def test_create(setup_teardown_file):
    """Group is created if it doesn"t exist."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp2 = grp.require_group("foo")
    assert isinstance(grp2, Group)
    assert grp2.name == "/test/foo"


def test_require_exception(setup_teardown_file):
    """Opening conflicting object results in TypeError."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp.create_dataset("foo", (1,))

    with pytest.raises(TypeError):
        grp.require_group("foo")


# TODO uncomment when deletion is implemented
# Feature: Objects can be unlinked via "del" operator
# def test_delete(setup_teardown_file):
#     """Object deletion via "del"."""
#
#     f = setup_teardown_file
#     grp = f.create_group("test")
#     grp.create_group("foo")
#
#     assert "foo" in grp
#     del grp["foo"]
#     assert "foo" not in grp
#
# def test_nonexisting(setup_teardown_file):
#     """Deleting non-existent object raises KeyError."""
#     f = setup_teardown_file
#     grp = f.create_group("test")
#
#     with pytest.raises(KeyError):
#         del grp["foo"]
#
# def test_readonly_delete_exception(setup_teardown_file):
#     """Deleting object in readonly file raises KeyError."""
#     f = setup_teardown_file
#     f.close()
#
#     f = File(pytest.TESTFILE, "r")
#
#     with pytest.raises(KeyError):
#         del f["foo"]


# Feature: Objects can be opened via indexing syntax obj[name]

def test_open(setup_teardown_file):
    """Simple obj[name] opening."""
    f = setup_teardown_file
    grp = f.create_group("test")
    grp2 = grp.create_group("foo")

    grp3 = grp["foo"]
    grp4 = grp["foo/"]

    assert grp2 == grp3
    assert grp2 == grp4


def test_open_deep(setup_teardown_file):
    """Simple obj[name] opening."""
    f = setup_teardown_file
    grp = f.create_group("test")
    grp2 = grp.create_group("a")
    grp3 = grp2.create_group("b")

    grp4 = grp["a/b"]

    assert grp3 == grp4



def test_nonexistent(setup_teardown_file):
    """Opening missing objects raises KeyError."""
    f = setup_teardown_file

    with pytest.raises(KeyError):
        f["foo"]


# Feature: The Python "in" builtin tests for containership
def test_contains(setup_teardown_file):
    """'in' builtin works for containership."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp.create_group("b")

    assert "b" in grp
    assert not "c" in grp

    with pytest.raises(NotImplementedError):
        assert "/b" in  grp


def test_contains_deep(setup_teardown_file):
    """'in' builtin works for containership."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp2 = grp.create_group("a")
    grp3 = grp2.create_group("b")

    assert "a/b" in grp


# TODO uncomment this when close is implemented
# def test_exc(setup_teardown_file):
#     """'in' on closed group returns False."""
#     f = setup_teardown_file

#     f.create_group("a")
#     f.close()

#     assert not "a" in f

def test_empty(setup_teardown_file):
    """Empty strings work properly and aren"t contained."""
    f = setup_teardown_file
    grp = f.create_group("test")

    assert not "" in grp

def test_dot(setup_teardown_file):
    """Current group "." is always contained."""
    f = setup_teardown_file

    assert "." in  f

def test_root(setup_teardown_file):
    """Root group (by itself) is contained."""
    f = setup_teardown_file
    grp = f.create_group("test")

    with pytest.raises(NotImplementedError):
        assert "/" in  grp

def test_trailing_slash(setup_teardown_file):
    """Trailing slashes are unconditionally ignored."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp.create_group("a")
    assert "a/" in grp
    assert "a//" in grp
    assert "a////" in grp




# Feature: Standard Python 3 .keys, .values, etc. methods are available
def test_keys(setup_teardown_file):
    """.keys provides a key view."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp.create_group("a")
    grp.create_group("b")
    grp.create_group("c")
    grp.create_group("d")

    assert isinstance(grp.keys(), KeysView)
    assert sorted(list(grp.keys())) == ["a", "b", "c", "d"]

def test_values(setup_teardown_file):
    """.values provides a value view."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grpa = grp.create_group("a")
    grpb = grp.create_group("b")
    grpc = grp.create_group("c")
    grpd = grp.create_group("d")

    assert isinstance(grp.values(), ValuesView)
    assert list(grp.values()) == [grpa, grpb, grpc, grpd]

def test_items(setup_teardown_file):
    """.items provides an item view."""
    f = setup_teardown_file
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
    f = setup_teardown_file
    grp = f.create_group("test")

    grp.create_group("a")
    grp.create_group("b")
    grp.create_group("c")
    grp.create_group("d")

    lst = [x for x in grp]
    assert lst == ["a", "b", "c", "d"]

def test_iter_zero(setup_teardown_file):
    """Iteration works properly for the case with no group members."""
    f = setup_teardown_file
    grp = f.create_group("test")

    lst = [x for x in grp]
    assert lst == []


# Feature: Equal

def test_eq(setup_teardown_file):
    """Test equal."""
    f = setup_teardown_file
    grp = f.create_group("test")

    grp2 = grp.create_group("a")

    assert grp2 == grp2
    assert grp != grp2