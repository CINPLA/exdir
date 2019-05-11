from . import exdir_object as exob


class Raw(exob.Object):
    """
    Raw objects are simple folders with any content.

    Raw objects currently have no features apart from showing their path.
    """
    def __init__(self, root_directory, parent_path, object_name, file):
        super(Raw, self).__init__(
            root_directory=root_directory,
            parent_path=parent_path,
            object_name=object_name,
            file=file
        )
