# This file is part of Exdir, the Experimental Directory Structure.
#
# Copyright 2017 Simen Tennøe
#
# License: MIT, see "LICENSE" file for the full license terms.
#
# This file contains code from h5py, a Python interface to the HDF5 library,
# licensed under a standard 3-clause BSD license
# with copyright Andrew Collette and contributors.
# See http://www.h5py.org and the "3rdparty/h5py-LICENSE" file for details.


import pytest
import numpy as np
import os
import quantities as pq

from exdir.core import Attribute, File, Dataset, plugin

from exdir.plugins.quantities import convert_quantities, convert_back_quantities


def test_create_quantities_data(setup_teardown_file):
    plugin.load_plugins()

    f = setup_teardown_file[3]
    grp = f.create_group("test")

    testdata = np.array([1, 2, 3]) * pq.J
    dset = grp.create_dataset('data', data=testdata)

    outdata = dset[()]

    assert isinstance(outdata, pq.Quantity)
    assert np.all(outdata == testdata)
    assert outdata.dtype == testdata.dtype

    outdata = dset[0]

    assert isinstance(outdata, pq.Quantity)
    assert np.all(outdata == testdata[0])
    assert outdata.dtype == testdata.dtype



def test_assign_quantities(setup_teardown_file):
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    testdata = np.array([1,2,3]) * pq.J
    dset = grp.create_dataset('data', data=testdata)

    outdata = f['test']["data"][()]

    assert isinstance(outdata, pq.Quantity)
    assert np.all(outdata == testdata)
    assert outdata.dtype == testdata.dtype


def test_set_quantities(setup_teardown_file):
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    dset = grp.create_dataset('data', data=np.array([1]))

    testdata = np.array([1.1, 2, 3]) * pq.J
    dset.value = testdata
    outdata = f['test']["data"][()]

    assert isinstance(outdata, pq.Quantity)
    assert np.all(outdata == testdata)
    assert outdata.dtype == testdata.dtype



def test_mmap_quantities(setup_teardown_file):
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    testdata = np.array([1, 2, 3]) * pq.J
    dset = grp.create_dataset('data', data=testdata)

    dset[1] = 100

    tmp_file = np.load(str(setup_teardown_file[1] / "test" / "data" / "data.npy"))

    assert dset.data[1] == 100
    assert tmp_file[1] == 100


def test_require_quantities(setup_teardown_file):
    f = setup_teardown_file[3]
    grp = f.create_group("test")

    testdata = np.array([1, 2, 3]) * pq.J
    dset = grp.create_dataset('data', data=testdata)

    dset2 = grp.require_dataset('data', data=testdata)

    assert dset == dset2
    assert np.all(dset[:] == testdata)
    assert np.all(dset2[:] == testdata)
    assert isinstance(dset[:], pq.Quantity)




#
def test_convert_quantities():
    pq_value = pq.Quantity(1, "m")
    result = convert_quantities(pq_value)
    assert result == {"value": 1, "unit": "m"}

    pq_value = pq.Quantity([1, 2, 3], "m")
    result = convert_quantities(pq_value)
    assert result == {"value": [1, 2, 3], "unit": "m"}

    result = convert_quantities(np.array([1, 2, 3]))
    assert result == [1, 2, 3]

    result = convert_quantities(1)
    assert result == 1

    result = convert_quantities(2.3)
    assert result == 2.3

    pq_value = pq.UncertainQuantity([1, 2], "m", [3, 4])
    result = convert_quantities(pq_value)
    assert result == {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}

    pq_values = {"quantity": pq.Quantity(1, "m"),
                 "uq_quantity": pq.UncertainQuantity([1, 2], "m", [3, 4])}
    result = convert_quantities(pq_values)
    assert(result == {"quantity": {"unit": "m", "value": 1},
                      "uq_quantity": {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}})

    pq_values = {"list": [1, 2, 3], "quantity": pq.Quantity(1, "m")}
    pq_dict = {"list": [1, 2, 3], "quantity": {"unit": "m", "value": 1}}
    result = convert_quantities(pq_values)
    assert result == pq_dict


def test_convert_back_quantities():
    pq_dict = {"value": 1, "unit": "m"}
    result = convert_back_quantities(pq_dict)
    assert result == pq.Quantity(1, "m")

    pq_dict = {"value": [1, 2, 3], "unit": "m"}
    result = convert_back_quantities(pq_dict)
    assert np.array_equal(result, pq.Quantity([1, 2, 3], "m"))

    pq_dict = {"value": [1, 2, 3]}
    result = convert_back_quantities(pq_dict)
    assert result == pq_dict

    result = convert_back_quantities(1)
    assert result == 1

    result = convert_back_quantities(2.3)
    assert result == 2.3

    pq_dict = {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}
    result = convert_back_quantities(pq_dict)
    pq_value = pq.UncertainQuantity([1, 2], "m", [3, 4])

    assert isinstance(result, pq.UncertainQuantity)
    assert result.magnitude.tolist() == pq_value.magnitude.tolist()
    assert result.dimensionality.string == pq_value.dimensionality.string
    assert result.uncertainty.magnitude.tolist() == pq_value.uncertainty.magnitude.tolist()

    pq_dict = {"quantity": {"unit": "m", "value": 1},
               "uq_quantity": {"unit": "m", "uncertainty": [3, 4], "value": [1.0, 2.0]}}
    pq_values = {"quantity": pq.Quantity(1, "m"),
                 "uq_quantity": pq.UncertainQuantity([1, 2], "m", [3, 4])}
    result = convert_back_quantities(pq_values)
    assert result == pq_values

    pq_values = {"list": [1, 2, 3], "quantity": {"unit": "m", "value": 1}}
    result = convert_back_quantities(pq_values)
    assert result == {"list": [1, 2, 3], "quantity": pq.Quantity(1, "m")}