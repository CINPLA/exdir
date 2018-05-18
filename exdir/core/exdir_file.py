import os
import shutil
import pathlib
import warnings

import exdir
from . import exdir_object as exob
from .group import Group
from .. import utils


class File(Group):
    """
    Exdir file object.
    A File is a special type of :class:`.Group`.
    See :class:`.Group` for documentation of inherited functions.

    To create a File, call the File constructor with the name of the File you wish to create:

        >>> import exdir
        >>> import numpy as np
        >>> f = exdir.File("mytestfile.exdir")

    The :code:`File` object :code:`f` now points to the root folder in the exdir file
    structure.
    You can add groups and datasets to it as follows:

        >>> my_group = f.require_group("my_group")
        >>> a = np.arange(100)
        >>> dset = f.require_dataset("my_data", data=a)

    The data is immediately written to disk.

    Parameters
    ----------
    directory:
        Name of the directory to be opened or created as an Exdir File.
    mode: str, optional
        A file mode string that defines the read/write behavior.
        See open() for information about the different modes.
    allow_remove: bool
        Set to True if you want mode 'w' to remove existing trees if they
        exist. This False by default to avoid removing entire directory
        trees by mistake.
    name_validation: str, function, optional
        Set the validation mode for names.
        Can be a function that takes a name and returns True if the name
        is valid or one of the following built-in validation modes:

        - 'strict': only allow numbers, lowercase letters, underscore (_) and dash (-)
        - 'simple': allow numbers, lowercase letters, uppercase letters, underscore (_) and dash (-), check if any file exists with same name in any case.
        - 'thorough': verify if name is safe on all platforms, check if any file exists with same name in any case.
        - 'none': allows any filename

        The default is 'thorough'.
    plugins: list, optional
        A list of instantiated plugins or modules with a plugins()
        function that returns a list of plugins.

    """

    def __init__(self, directory, mode=None, allow_remove=False,
                 name_validation=None, plugins=None, validate_name=None):
        if validate_name is not None:
            warnings.warn("validate_name is deprecated. Use name_validation instead.")
            name_validation = name_validation or validate_name

        directory = pathlib.Path(directory) #.resolve()
        if directory.suffix != ".exdir":
            directory = directory.with_suffix(directory.suffix + ".exdir")
        mode = mode or 'a'
        recognized_modes = ['a', 'r', 'r+', 'w', 'w-', 'x', 'a']
        if mode not in recognized_modes:
            raise ValueError(
                "IO mode {} not recognized, "
                "mode must be one of {}".format(mode, recognized_modes)
            )

        plugin_manager = exdir.plugin_interface.plugin_interface.Manager(plugins)

        if mode == "r":
            self.io_mode = self.OpenMode.READ_ONLY
        else:
            self.io_mode = self.OpenMode.READ_WRITE

        super(File, self).__init__(
            root_directory=directory,
            parent_path=pathlib.PurePosixPath(""),
            object_name="",
            io_mode=self.io_mode,
            name_validation=name_validation,
            plugin_manager=plugin_manager
        )

        already_exists = directory.exists()
        if already_exists:
            if not exob.is_nonraw_object_directory(directory):
                raise FileExistsError(
                    "Path '{}' already exists, but is not a valid exdir file.".format(directory)
                )
            # TODO consider extracting this function to avoid cyclic imports
            if self.meta[exob.EXDIR_METANAME][exob.TYPE_METANAME] != exob.FILE_TYPENAME:
                raise FileExistsError(
                    "Path '{}' already exists, but is not a valid exdir file.".format(directory)
                )

        should_create_directory = False

        if mode == "r":
            if not already_exists:
                raise IOError("File " + str(directory) + " does not exist.")
        elif mode == "r+":
            if not already_exists:
                raise IOError("File " + str(directory) + " does not exist.")
        elif mode == "w":
            if already_exists:
                if allow_remove:
                    shutil.rmtree(str(directory))  # NOTE str needed for Python 3.5
                else:
                    raise FileExistsError(
                        "File {} already exists. We won't delete the entire tree "
                        "by default. Add allow_remove=True to override.".format(directory)
                    )
            should_create_directory = True
        elif mode == "w-" or mode == "x":
            if already_exists:
                raise IOError("File " + str(directory) + " already exists.")
            should_create_directory = True
        elif mode == "a":
            if not already_exists:
                should_create_directory = True

        if should_create_directory:
            self.name_validation(directory.parent, directory.name)
            exob._create_object_directory(directory, exob.FILE_TYPENAME)

    def close(self):
        """
        Closes the File object.
        Currently, this has no effect because all data is immediately written to disk.
        """
        # yeah right, as if we would create a real file format
        pass

    def create_group(self, name):
        """
        Create a group with the given name or absolute path.

        See :class:`.Group` for more details.

        Note
        ----
        Creating groups with absolute paths is only allowed on File objects and
        not on Group objects in general.
        """
        path = utils.path.remove_root(name)

        return super().create_group(path)

    def require_group(self, name):
        """
        Open an existing subgroup or create one if it does not exist.

        See :class:`.Group` for more details.

        Note
        ----
        Creating groups with absolute paths is only allowed on File objects and
        not on Group objects in general.
        """
        path = utils.path.remove_root(name)

        return super().require_group(path)

    def __getitem__(self, name):
        path = utils.path.remove_root(name)
        if len(path.parts) < 1:
            return self
        return super().__getitem__(path)

    def __contains__(self, name):
        path = utils.path.remove_root(name)
        return super().__contains__(path)
