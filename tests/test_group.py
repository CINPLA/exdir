import os
import pytest

from exdir.core import Group, File

# # tests for Group class
# def test_group_init(setup_teardown_folder):
#     group = Group(pytest.TESTDIR, "", "test_object", io_mode=None)

#     assert group.root_directory == pytest.TESTDIR
#     assert group.object_name == "test_object"
#     assert group.parent_path == ""
#     assert group.io_mode is None
#     assert group.relative_path == os.path.join("", "test_object")
#     assert group.name == "/" + os.path.join("", "test_object")


# New groups can be created via .create_group method

def test_create_group(setup_teardown_file):
    """Simple .create_group call."""

    f = setup_teardown_file

    grp = f.create_group("foo")
    assert isinstance(grp, Group)


def test_create_group_absolute(setup_teardown_file):
    """Starting .create_group argument with /."""

    f = setup_teardown_file

    grp = f.create_group("/a")

    with pytest.raises(NotImplementedError):
        grp.create_group("/b")


# # TODO update this test when it is implemented
# def test_create_intermediate(setup_teardown_file):
#     """Intermediate groups can be created automatically."""
#     f = setup_teardown_file

#     with pytest.raises(NotImplementedError):
#         grp = f.create_group("foo/bar/baz")

#     # assert grp.name == "/foo/bar/baz"


# def test_create_exception(setup_teardown_file):
#     """Name conflict causes group creation to fail with IOError."""
#     f = setup_teardown_file
#     f.create_group("foo")
#     with pytest.raises(NameError):
#         f.create_group("foo")


# # Feature: Groups can be auto-created, or opened via .require_group
# def test_open_existing(setup_teardown_file):
#     """Existing group is opened and returned."""
#     f = setup_teardown_file

#     grp = f.create_group("foo")
#     grp2 = f.require_group("foo")
#     assert grp == grp2


# def test_create(setup_teardown_file):
#     """Group is created if it doesn"t exist."""
#     f = setup_teardown_file

#     grp = f.require_group("foo")
#     assert isinstance(grp, Group)
#     assert grp.name == "/foo"


# def test_require_exception(setup_teardown_file):
#     """Opening conflicting object results in TypeError."""
#     f = setup_teardown_file
#     f.create_dataset("foo", (1,))

#     with pytest.raises(TypeError):
#         f.require_group("foo")


# # TODO uncomment when deletion is implemented
# # Feature: Objects can be unlinked via "del" operator
# # def test_delete(setup_teardown_file):
# #     """Object deletion via "del"."""
# #
# #     f = setup_teardown_file
# #     f.create_group("foo")
# #     assert "foo" in f
# #     del f["foo"]
# #     assert "foo" not in f
# #
# # def test_nonexisting(setup_teardown_file):
# #     """Deleting non-existent object raises KeyError."""
# #     f = setup_teardown_file
# #
# #     with pytest.raises(KeyError):
# #         del f["foo"]
# #
# # def test_readonly_delete_exception(setup_teardown_file):
# #     """Deleting object in readonly file raises KeyError."""
# #     f = setup_teardown_file
# #     f.close()
# #
# #     f = File(pytest.TESTFILE, "r")
# #
# #     with pytest.raises(KeyError):
# #         del f["foo"]


# # Feature: Objects can be opened via indexing syntax obj[name]

# def test_open(setup_teardown_file):
#     """Simple obj[name] opening."""
#     f = setup_teardown_file

#     grp = f.create_group("foo")
#     grp2 = f["foo"]
#     grp3 = f["/foo"]

#     assert grp, grp2
#     assert grp, grp3


# def test_nonexistent(setup_teardown_file):
#     """Opening missing objects raises KeyError."""
#     f = setup_teardown_file

#     with pytest.raises(KeyError):
#         f["foo"]


# # Feature: The Python "in" builtin tests for containership
# def test_contains(setup_teardown_file):
#     """'in' builtin works for containership (byte and Unicode)."""
#     f = setup_teardown_file

#     f.create_group("a")
#     # assert "a" in  f
#     assert "a" in  f
#     # assert not "b" in f

# def test_exc(setup_teardown_file):
#     """'in' on closed group returns False."""
#     f = setup_teardown_file

#     f.create_group("a")
#     f.close()
#     assert not b"a" in f
#     assert not "a" in f

# def test_empty(setup_teardown_file):
#     """Empty strings work properly and aren"t contained."""
#     f = setup_teardown_file

#     assert not "" in f
#     assert not b"" in f

# def test_dot(setup_teardown_file):
#     """Current group "." is always contained."""
#     f = setup_teardown_file

#     assert b"." in  f
#     assert "." in  f

# def test_root(setup_teardown_file):
#     """Root group (by itself) is contained."""
#     f = setup_teardown_file

#     assert b"/" in  f
#     assert "/" in  f

# def test_trailing_slash(setup_teardown_file):
#     """Trailing slashes are unconditionally ignored."""
#     f = setup_teardown_file

#     f.create_group("group")
#     f["dataset"] = 42
#     assert "/group/" in  f
#     assert "group/" in  f
#     assert "/dataset/" in  f
#     assert "dataset/" in  f

# def test_oddball_paths(setup_teardown_file):
#     """Technically legitimate (but odd-looking) paths."""
#     f = setup_teardown_file

#     f.create_group("x/y/z")
#     f["dset"] = 42
#     assert "/" in  f
#     assert "//" in  f
#     assert "///" in  f
#     assert ".///" in  f
#     assert "././/" in  f
#     grp = f["x"]
#     assert ".//x/y/z" in  f
#     assert not ".//x/y/z"in grp
#     assert "x///" in  f
#     assert "./x///" in  f
#     assert "dset///" in  f
#     assert "/dset//" in  f
