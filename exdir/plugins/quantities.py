# Needed for quantities
from __future__ import absolute_import

import exdir
import quantities as pq
import numpy as np

from collections import defaultdict


def convert_back_quantities(value):
    """Convert quantities back from dictionary."""
    result = value
    if isinstance(value, dict):
        if "unit" in value and "value" in value and "uncertainty" in value:
            try:
                result = pq.UncertainQuantity(value["value"],
                                              value["unit"],
                                              value["uncertainty"])
            except Exception:
                pass
        elif "unit" in value and "value" in value:
            try:
                result = pq.Quantity(value["value"], value["unit"])
            except Exception:
                pass
        else:
            try:
                for key, value in result.items():
                    result[key] = convert_back_quantities(value)
            except AttributeError:
                pass

    return result


def convert_quantities(value):
    """Convert quantities to dictionary."""

    result = value
    if isinstance(value, pq.Quantity):
        result = {
            "value": value.magnitude.tolist(),
            "unit": value.dimensionality.string
        }
        if isinstance(value, pq.UncertainQuantity):
            assert value.dimensionality == value.uncertainty.dimensionality
            result["uncertainty"] = value.uncertainty.magnitude.tolist()
    elif isinstance(value, np.ndarray):
        result = value.tolist()
    elif isinstance(value, np.integer):
        result = int(value)
    elif isinstance(value, np.float64):
        result = float(value)
    else:
        # try if dictionary like objects can be converted if not return the
        # original object
        # Note, this might fail if .items() returns a strange combination of
        # objects
        try:
            new_result = {}
            for key, val in value.items():
                new_key = convert_quantities(key)
                new_result[new_key] = convert_quantities(val)
            result = new_result
        except AttributeError:
            pass

    return result


class DatasetPlugin(exdir.plugin_interface.Dataset):
    def prepare_read(self, dataset_data):
        values = dataset_data.data
        attrs = dataset_data.attrs

        if "unit" in attrs:
            item_dict = {
                "value": values,
                "unit": attrs["unit"]
            }
            if "uncertainty" in attrs:
                item_dict["uncertainty"] = attrs["uncertainty"]

            values = convert_back_quantities(item_dict)

        dataset_data.data = values

        return dataset_data

    def prepare_write(self, dataset_data):
        data = dataset_data.data
        attrs = {}

        meta = dataset_data.meta

        if isinstance(data, pq.Quantity):
            # TODO consider adding a helper class that wraps defaultdict and converts back again
            if "plugins" not in meta:
                meta["plugins"] = {}

            if "quantities" not in meta["plugins"]:
                meta["plugins"]["quantities"] = {}

            meta["plugins"]["quantities"]["required"] = True
            result = data.magnitude
            attrs["unit"] = data.dimensionality.string
            if isinstance(data, pq.UncertainQuantity):
                attrs["uncertainty"] = data.uncertainty
        else:
            result = data

        dataset_data.data = data
        dataset_data.attrs = attrs
        dataset_data.meta = dict(meta)

        return dataset_data


class AttributePlugin(exdir.plugin_interface.Attribute):
    def prepare_read(self, attribute_data):
        attribute_data.attrs = convert_back_quantities(attribute_data.attrs)
        return attribute_data

    def prepare_write(self, attribute_data):
        attribute_data.attrs = convert_quantities(attribute_data.attrs)
        return attribute_data


def plugins():
    return [exdir.plugin_interface.Plugin(
        "quantities",
        dataset_plugins=[DatasetPlugin()],
        attribute_plugins=[AttributePlugin()],
        read_before=["numpy_attributes"],
        write_before=["numpy_attributes"]
    )]
