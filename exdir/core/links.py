from . import exdir_file
from .exdir_object import Object, is_nonraw_object_directory
from .constants import *


class Link(Object):
    """
    Super class for link objects
    """
    def __init__(self, path):
        self.path = path

    @property
    def _link(self):
        return {TYPE_METANAME: LINK_TYPENAME}

    def __eq__(self, other):
        return self._link.get(LINK_METANAME) == other._link.get(LINK_METANAME)


class SoftLink(Link):
    def __init__(self, path):
        super(SoftLink, self).__init__(
            path=path
        )

    @property
    def _link(self):
        result = {
            TYPE_METANAME: LINK_TYPENAME,
            LINK_METANAME: {
                TYPE_METANAME: LINK_SOFTNAME,
                LINK_TARGETNAME: self.path
             }
        }
        return result

    def __repr__(self):
        return "Exdir SoftLink '{}' at {}".format(self.path, id(self))


class ExternalLink(Link):
    def __init__(self, filename, path):
        super(ExternalLink, self).__init__(
            path=path
        )
        self.filename = filename

    @property
    def _link(self):
        result = {
            TYPE_METANAME: LINK_TYPENAME,
            LINK_METANAME: {
                TYPE_METANAME: LINK_EXTERNALNAME,
                LINK_TARGETNAME: self.path,
                LINK_FILENAME: str(self.filename)
             }
        }
        return result

    def __repr__(self):
        return "Exdir SoftLink '{}' at {}".format(self.path, id(self))


class Reference(object):
    def __init__(self, path):
        self.path = path


class RegionReference(Reference):
    def __init__(self, path).
        self.path = path
