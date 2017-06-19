import os
import shutil

from . import exdir_object as exob
from .group import Group


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

        naming_rule = naming_rule or 'simple'
        if naming_rule == 'simple':
            self.naming_rule = self.NamingRule.SIMPLE
        elif naming_rule == 'strict':
            self.naming_rule = self.NamingRule.STRICT
        elif naming_rule == 'thorough':
            self.naming_rule = self.NamingRule.THOROUGH
        elif naming_rule == 'none':
            self.naming_rule = self.NamingRule.NONE
        else:
            raise ValueError('IO name rule "' + naming_rule + '" not recognized,' +
                             'name rule must be one of "strict", "simple", ' +
                             '"thorough", "none"')

        super(File, self).__init__(root_directory=directory,
                                   parent_path="", object_name="",
                                   io_mode=self.io_mode,
                                   naming_rule=self.naming_rule)

        already_exists = os.path.exists(directory)
        if already_exists:
            if not exob._is_nonraw_object_directory(directory):
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

        valid_characters = ("abcdefghijklmnopqrstuvwxyz1234567890_-.")
        if should_create_directory:
            path, name = os.path.split(directory)
            if path == "":
                path = "."

            if self.naming_rule == self.NamingRule.THOROUGH:
                raise NotImplementedError

            elif self.naming_rule == self.NamingRule.STRICT:
                for char in name:
                    if char not in valid_characters:
                        raise NameError("Name contains invalid character '" + char + "'.\n" +
                                        "Valid characters are:\n" + valid_characters)

            elif self.naming_rule == self.NamingRule.SIMPLE:
                for char in name:
                    if char.lower() not in valid_characters:
                        raise FileExistsError("Name contains invalid character '" + char + "'.\n" +
                                              "Valid characters are:\n" + valid_characters)

                    for item in os.listdir(path):
                        if name.lower() == item.lower():
                            raise NameError("A directory with name (case independent) '" + name +
                                            "' already exists and cannot be made according " +
                                            "to the naming rule 'simple'.")

            invalid_names = [exob.META_FILENAME,
                             exob.ATTRIBUTES_FILENAME,
                             exob.RAW_FOLDER_NAME]

            if name in invalid_names:
                raise NameError("Name cannot be '" + name + "'.")

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
