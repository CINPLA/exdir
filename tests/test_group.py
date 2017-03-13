import pytest
import os

from exdir.core import Group

# tests for Group class


def test_group_init(setup_teardown_folder):
    group = Group(pytest.TESTDIR, "", "test_object", io_mode=None)

    assert(group.root_directory == pytest.TESTDIR)
    assert(group.object_name == "test_object")
    assert(group.parent_path == "")
    assert(group.io_mode is None)
    assert(group.relative_path == os.path.join("", "test_object"))
    assert(group.name == os.sep + os.path.join("", "test_object"))
