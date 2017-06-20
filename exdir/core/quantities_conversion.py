import quantities as pq
import numpy as np
import yaml


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
