from . import abstract_object


class Raw(abstract_object.AbstractObject):
    """
    Raw objects are simple folders with any content.

    Raw objects currently have no features apart from showing their path.
    """
    def __init__(self, root_directory, parent_path, object_name, io_mode=None):
        super(Raw, self).__init__(root_directory=root_directory,
                                  parent_path=parent_path,
                                  object_name=object_name,
                                  io_mode=io_mode)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return False
