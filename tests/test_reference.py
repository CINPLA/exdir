import pytest
import exdir


def test_reference(setup_teardown_file):
    """ Indexing a reference dataset returns a exdir.Reference instance """
    f = setup_teardown_file[3]
    dset = f.create_dataset('x', (1,), dtype=exdir.ref_dtype)
    dset[0] = f.ref
    assertEqual(type(dset[0]), exdir.Reference)

# def test_regref(self):
#     """ Indexing a region reference dataset returns a exdir.RegionReference
#     """
#     dset1 = f.create_dataset('x', (10,10))
#     regref = dset1.regionref[...]
#     dset2 = f.create_dataset('y', (1,), dtype=exdir.regionref_dtype)
#     dset2[0] = regref
#     assertEqual(type(dset2[0]), exdir.RegionReference)
#
# def test_scalar(self):
#     """ Indexing returns a real Python object on scalar datasets """
#     dset = f.create_dataset('x', (), dtype=exdir.ref_dtype)
#     dset[()] = f.ref
#     assertEqual(type(dset[()]), exdir.Reference)
#
#
# def test_reference(self):
#     """ Objects can be opened by HDF5 object reference """
#     grp = f.create_group('foo')
#     grp2 = f[grp.ref]
#     assertEqual(grp2, grp)
#
# def test_reference_numpyobj(self):
#     """ Object can be opened by numpy.object_ containing object ref
#     Test for issue 181, issue 202.
#     """
#     g = f.create_group('test')
#
#     dt = np.dtype([('a', 'i'),('b', exdir.ref_dtype)])
#     dset = f.create_dataset('test_dset', (1,), dt)
#
#     dset[0] =(42,g.ref)
#     data = dset[0]
#     assertEqual(f[data[1]], g)
#
# def test_invalid_ref(self):
#     """ Invalid region references should raise ValueError """
#
#     ref = exdir.h5r.Reference()
#
#     with assertRaises(ValueError):
#         f[ref]
#
#     f.create_group('x')
#     ref = f['x'].ref
#     del f['x']
#
#     with assertRaises(ValueError):
#         f[ref]

# TODO: check that regionrefs also work with __getitem__
