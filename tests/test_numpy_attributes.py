import exdir

import pytest
import os
import numpy as np
import quantities as pq


def test_simple(setup_teardown_folder):
    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[exdir.plugins.numpy_attributes])
    f.attrs["array"] = np.array([1, 2, 3])
    print(f.attrs["array"])
    print(type(f.attrs["array"]))
    f.close()

    f = open(setup_teardown_folder[1] / "attributes.yaml", "r")

    print("-------------------")
    print(f.read())
    print("-------------------")
    f.close()



def test_with_quantities(setup_teardown_folder):
    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[exdir.plugins.numpy_attributes, exdir.plugins.quantities])
    f.attrs["array"] = np.array([1, 2, 3]) * pq.m
    print(f.attrs["array"])
    print(type(f.attrs["array"]))
    f.close()

    f = open(setup_teardown_folder[1] / "attributes.yaml", "r")

    print("-------------------")
    print(f.read())
    print("-------------------")
    f.close()
