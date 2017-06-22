import os
import shutil
import pathlib

from . import exdir_object as exob
from .group import Group
from .. import utils


class File(Group):
    """Exdir file object."""

    def __init__(self, directory, mode=None, allow_remove=False,
                 validate_name=None):
        directory = pathlib.Path(directory).resolve()
        if directory.suffix != ".exdir":
            directory = directory.with_suffix(directory.suffix + ".exdir")
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
                                   parent_path=pathlib.PurePosixPath(""),
                                   object_name="",
                                   io_mode=self.io_mode,
                                   validate_name=validate_name)

        already_exists = os.path.exists(directory)
        if already_exists:
            if not exob.is_nonraw_object_directory(directory):
                raise FileExistsError("Path '" + str(directory) +
                                      "' already exists, but is not a valid " +
                                      "exdir file.")
            # TODO consider extracting this function to avoid cyclic imports
            if self.meta[exob.EXDIR_METANAME][exob.TYPE_METANAME] != exob.FILE_TYPENAME:
                raise FileExistsError("Path '" + str(directory) +
                                      "' already exists, but is not a valid " +
                                      "exdir file.")

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
                    shutil.rmtree(directory)
                else:
                    raise FileExistsError(
                        "File " + str(directory) + " already exists. We won't delete the entire tree" +
                        " by default. Add allow_remove=True to override."
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
            self.validate_name(directory.parent, directory.name)
            exob._create_object_directory(directory, exob.FILE_TYPENAME)

    def close(self):
        # yeah right, as if we would create a real file format
        pass

    def create_group(self, name):
        path = utils.path.remove_root(name)

        return super().create_group(path)

    def require_group(self, name):
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
