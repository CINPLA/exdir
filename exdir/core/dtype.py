from numpy import dtype
from .links import Reference, RegionReference

ref_dtype = dtype(str, metadata={'ref': Reference})
regionref_dtype = dtype(str, metadata={'ref': RegionReference})


def special_dtype(**kwds):
    """ Create a new h5py "special" type.  Only one keyword may be given.
    Legal keywords are:
    vlen = basetype
        Base type for HDF5 variable-length datatype. This can be Python
        str type or instance of np.dtype.
        Example: special_dtype( vlen=str )
    enum = (basetype, values_dict)
        Create a NumPy representation of an HDF5 enumerated type.  Provide
        a 2-tuple containing an (integer) base dtype and a dict mapping
        string names to integer values.
    ref = Reference | RegionReference
        Create a NumPy representation of an HDF5 object or region reference
        type.
    """

    if len(kwds) != 1:
        raise TypeError("Exactly one keyword may be provided")

    name, val = kwds.popitem()

    if name == 'vlen':

        return dtype('O', metadata={'vlen': val})

    if name == 'enum':

        try:
            dt, enum_vals = val
        except TypeError:
            raise TypeError("Enums must be created from a 2-tuple (basetype, values_dict)")

        return enum_dtype(enum_vals, dt)

    if name == 'ref':

        if val not in (Reference, RegionReference):
            raise ValueError("Ref class must be Reference or RegionReference")

        return ref_dtype if (val is Reference) else regionref_dtype

    raise TypeError('Unknown special type "%s"' % name)


def check_string_dtype(dt):
    """If the dtype represents an HDF5 string, returns a string_info object.
    The returned string_info object holds the encoding and the length.
    The encoding can only be 'utf-8' or 'ascii'. The length may be None
    for a variable-length string, or a fixed length in bytes.
    Returns None if the dtype does not represent an HDF5 string.
    """
    vlen_kind = check_vlen_dtype(dt)
    if vlen_kind is unicode:
        return string_info('utf-8', None)
    elif vlen_kind is bytes:
        return string_info('ascii', None)
    elif dt.kind == 'S':
        enc = (dt.metadata or {}).get('h5py_encoding', 'ascii')
        return string_info(enc, dt.itemsize)
    else:
        return None


def check_enum_dtype(dt):
    """If the dtype represents an HDF5 enumerated type, returns the dictionary
    mapping string names to integer values.
    Returns None if the dtype does not represent an HDF5 enumerated type.
    """
    try:
        return dt.metadata.get('enum', None)
    except AttributeError:
        return None


def check_ref_dtype(dt):
    """If the dtype represents an HDF5 reference type, returns the reference
    class (either Reference or RegionReference).
    Returns None if the dtype does not represent an HDF5 reference type.
    """
    try:
        return dt.metadata.get('ref', None)
    except AttributeError:
        return None


def check_dtype(**kwds):
    """ Check a dtype for h5py special type "hint" information.  Only one
    keyword may be given.
    vlen = dtype
        If the dtype represents an HDF5 vlen, returns the Python base class.
        Currently only builting string vlens (str) are supported.  Returns
        None if the dtype does not represent an HDF5 vlen.
    enum = dtype
        If the dtype represents an HDF5 enumerated type, returns the dictionary
        mapping string names to integer values.  Returns None if the dtype does
        not represent an HDF5 enumerated type.
    ref = dtype
        If the dtype represents an HDF5 reference type, returns the reference
        class (either Reference or RegionReference).  Returns None if the dtype
        does not represent an HDF5 reference type.
    """

    if len(kwds) != 1:
        raise TypeError("Exactly one keyword may be provided")

    name, dt = kwds.popitem()

    if name not in ('vlen', 'enum', 'ref'):
        raise TypeError('Unknown special type "%s"' % name)

    try:
        return dt.metadata[name]
    except TypeError:
        return None
    except KeyError:
        return None
