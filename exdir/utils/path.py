import pathlib


def name_to_asserted_group_path(name):
    path = pathlib.PurePosixPath(name)
    if path.is_absolute():
        raise NotImplementedError(
            "Absolute paths are currently not supported and unlikely to be implemented."
        )

    if len(path.parts) < 1 and str(name) != ".":
        raise NotImplementedError(
            "Getting an item on a group with path '" + name + "' " +
            "is not supported and unlikely to be implemented."
        )

    return path


def remove_root(name):
    path = pathlib.PurePosixPath(name)
    if path.is_absolute():
        path = path.relative_to(path.root)
    return path
