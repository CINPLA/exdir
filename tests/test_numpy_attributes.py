import exdir

import pytest
import os
import numpy as np
import quantities as pq
import exdir.plugins.quantities
import exdir.plugins.numpy_attributes

def test_simple(setup_teardown_folder):
    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[exdir.plugins.numpy_attributes])
    f.attrs["array"] = np.array([1, 2, 3])
    f.close()

    with open(str(setup_teardown_folder[1] / "attributes.yaml"), "r", encoding="utf-8") as f:
        content = "array:\n- 1\n- 2\n- 3\n"
        assert content == f.read()



def test_with_quantities(setup_teardown_folder):
    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[exdir.plugins.numpy_attributes, exdir.plugins.quantities])
    f.attrs["array"] = np.array([1, 2, 3]) * pq.m
    f.close()

    with open(str(setup_teardown_folder[1] / "attributes.yaml"), "r", encoding="utf-8")  as f:
        content = 'array:\n  value:\n  - 1.0\n  - 2.0\n  - 3.0\n  unit: "m"\n'

        # NOTE split and conversion to set is just because the order of the items is not important
        assert set(content.split("\n")) == set(f.read().split("\n"))


def test_with_quantities_reverse_order(setup_teardown_folder):
    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[exdir.plugins.quantities, exdir.plugins.numpy_attributes])
    f.attrs["array"] = np.array([1, 2, 3]) * pq.m
    f.close()

    with open(str(setup_teardown_folder[1] / "attributes.yaml"), "r")  as f:
        content = 'array:\n  value:\n  - 1.0\n  - 2.0\n  - 3.0\n  unit: "m"\n'

        # NOTE split and conversion to set is just because the order of the items is not important
        assert set(content.split("\n")) == set(f.read().split("\n"))
