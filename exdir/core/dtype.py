from numpy import dtype
from .links import Reference, RegionReference

ref_dtype = dtype('O', metadata={'ref': Reference})
regionref_dtype = dtype('O', metadata={'ref': RegionReference})


def special_dtype(**kwds):
    """ Create a new exdir "special" type.  Only one keyword may be given.
    Legal keywords are:
    vlen = basetype
        Base type for Exdir variable-length datatype. This can be Python
        str type or instance of np.dtype.
        Example: special_dtype( vlen=str )
    enum = (basetype, values_dict)
        Create a NumPy representation of an Exdir enumerated type.  Provide
        a 2-tuple containing an (integer) base dtype and a dict mapping
        string names to integer values.
    ref = Reference | RegionReference
        Create a NumPy representation of an Exdir object or region reference
        type.
    """

    if len(kwds) != 1:
        raise TypeError("Exactly one keyword may be provided")

    name, val = kwds.popitem()

    if name == 'ref':

        if val not in (Reference, RegionReference):
            raise ValueError("Ref class must be Reference or RegionReference")

        return ref_dtype if (val is Reference) else regionref_dtype

    raise TypeError('Unknown special type "%s"' % name)


def check_ref_dtype(dt):
    """If the dtype represents an Exdir reference type, returns the reference
    class (either Reference or RegionReference).
    Returns None if the dtype does not represent an Exdir reference type.
    """
    try:
        return dt.metadata.get('ref', None)
    except AttributeError:
        return None
