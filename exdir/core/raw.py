from . import exdir_object as exob


class Raw(exob.Object):
    """
    Raw objects are simple folders with any content.

    With exdir you can store raw data, containing any datatype you want in a `Raw` object.
    The typical usecase is raw data produced in a format that you want to keep
    alongside with data which is converted or processed
    and stored in exdir datasets.

    You can create `Raw` objects with::

        >>> import exdir
        >>> import numpy as np
        >>> f = exdir.File("myfile.exdir", "w")
        >>> raw = f.create_raw('raw_filename')

    Note that you may also use `require_raw`.
    Raw objects currently have no features apart from showing their path::

        >>> directory = raw.directory

    """
    def __init__(self, root_directory, parent_path, object_name, file):
        super(Raw, self).__init__(
            root_directory=root_directory,
            parent_path=parent_path,
            object_name=object_name,
            file=file
        )
