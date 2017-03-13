import pytest

from exdir.core import Attribute


def test_attr_init():
    attribute = Attribute("parent", "mode", "io_mode")

    assert(attribute.parent == "parent")
    assert(attribute.mode == "mode")
    assert(attribute.io_mode == "io_mode")
    assert(attribute.path == [])


# def test_attr_getitem():
#     attr_file = os.path.join(pytest.TESTPATH, "test_attrs")
#     _create_object_directory(attr_file, GROUP_TYPENAME)
#     attribute = Attribute("", Attribute.Mode.ATTRIBUTES, "io_mode")
