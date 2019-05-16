from .constants import *


class Link(object):
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
    base = '!exdir:ref'
    def __init__(self, path):
        if self.base in path:
            base, path = path.split(' ')
            assert base == self.base
        self.path = path
        self.ref = '{} {}'.format(self.base, path)


class RegionReference(Reference):
    base = '!exdir:regionref'
    def __init__(self, path):
        if self.base in path:
            base, path, region = path.split(' ')
            assert base == self.base
        self.path = path

    def __getitem__(self, args):
        self.ref = '{} {} {}'.format(self.base, self.path, args)
        return self
