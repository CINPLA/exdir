import exdir
import quantities as pq
import numpy as np
import yaml

def extract_quantity(data):
    attrs = {}
    if isinstance(data, pq.Quantity):
        result = data.magnitude
        attrs["unit"] = data.dimensionality.string
        if isinstance(data, pq.UncertainQuantity):
            attrs["uncertainty"] = data.uncertainty
    else:
        result = data
    return attrs, result


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
    elif isinstance(value, np.float):
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


class QuantitiesDatasetPlugin(exdir.plugin.Dataset):
    def prepare_read(self, values, attrs):
        if "unit" in attrs:
            item_dict = {
                "value": values,
                "unit": attrs["unit"]
            }
            if "uncertainty" in attrs:
                item_dict["uncertainty"] = attrs["uncertainty"]

            values = convert_back_quantities(item_dict)
        return values

    def prepare_write(self, value):
        return extract_quantity(value)



class QuantitiesAttributePlugin(exdir.plugin.Attribute):
    def preprocess_meta_data(self, attribute, meta_data):
        return convert_back_quantities(meta_data)
