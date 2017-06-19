import os
import shutil
import warnings

from . import exdir_object as exob
from .group import Group
from . import filename_validation


class File(Group):
    """Exdir file object."""

    def __init__(self, directory, mode=None, allow_remove=False,
                 naming_rule=None):
        if not directory.endswith(".exdir"):
            directory = directory + ".exdir"
        mode = mode or 'a'
        recognized_modes = ['a', 'r', 'r+', 'w', 'w-', 'x', 'a']
        if mode not in recognized_modes:
            raise ValueError('IO mode "' + mode + '" not recognized,' +
                             'mode must be one of {}'.format(recognized_modes))
        if mode == "r":
            self.io_mode = self.OpenMode.READ_ONLY
        else:
            self.io_mode = self.OpenMode.READ_WRITE

        super(File, self).__init__(root_directory=directory,
                                   parent_path="", object_name="",
                                   io_mode=self.io_mode,
                                   naming_rule=naming_rule)

        already_exists = os.path.exists(directory)
        if already_exists:
            if not exob.is_nonraw_object_directory(directory):
                raise FileExistsError("Path '" + directory +
                                      "' already exists, but is not a valid " +
                                      "exdir file.")
            if self.meta[exob.EXDIR_METANAME][exob.TYPE_METANAME] != exob.FILE_TYPENAME:  # TODO consider extracting this function to avoid cyclic imports
                raise FileExistsError("Path '" + directory +
                                      "' already exists, but is not a valid " +
                                      "exdir file.")

        should_create_directory = False

        if mode == "r":
            if not already_exists:
                raise IOError("File " + directory + " does not exist.")
        elif mode == "r+":
            if not already_exists:
                raise IOError("File " + directory + " does not exist.")
        elif mode == "w":
            if already_exists:
                if allow_remove:
                    shutil.rmtree(directory)
                else:
                    raise FileExistsError(
                        "File " + directory + " already exists. We won't delete the entire tree" +
                        " by default. Add allow_remove=True to override."
                    )
            should_create_directory = True
        elif mode == "w-" or mode == "x":
            if already_exists:
                raise IOError("File " + directory + " already exists.")
            should_create_directory = True
        elif mode == "a":
            if not already_exists:
                should_create_directory = True

        if should_create_directory:
            path, name = os.path.split(directory)
            if path == "":
                path = "."

            self.naming_rule(path, name)

            exob._create_object_directory(directory, exob.FILE_TYPENAME)

    def close(self):
        # yeah right, as if we would create a real file format
        pass

    def create_group(self, name):
        if name.startswith("/"):
            name = name[1:]

        return super().create_group(name)

    def require_group(self, name):
        if name.startswith("/"):
            name = name[1:]

        return super().require_group(name)

    def __getitem__(self, name):
        if name.startswith("/"):
            if name == "/":
                return self
            else:
                name = name[1:]

        return super().__getitem__(name)

    def __contains__(self, name):
        if name.startswith("/"):
            if name == "/":
                return True
            name = name[1:]

        return super().__contains__(name)
