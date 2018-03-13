import exdir
import quantities as pq
import numpy as np
import yaml


def convert_from_list(data):
    if isinstance(data, dict):
        try:
            for key, value in data.items():
                data[key] = convert_from_list(value)
        except AttributeError:
            pass
    elif isinstance(data, list):
        return np.array(data)
    return data


def convert_to_list(data):
    if isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.float):
        return float(data)
    else:
        try:
            new_result = {}
            for key, val in data.items():
                new_key = convert_to_list(key)
                new_result[new_key] = convert_to_list(val)
            return new_result
        except AttributeError:
            pass

    return data


class AttributePlugin(exdir.plugin_interface.Attribute):
    def prepare_write(self, attribute_data):
        attribute_data.attrs = convert_to_list(attribute_data.attrs)
        return attribute_data

    def prepare_read(self, attribute_data):
        attribute_data.attrs = convert_from_list(attribute_data.attrs)
        return attribute_data


def plugins():
    return [exdir.plugin_interface.Plugin(
        "numpy_attributes",
        attribute_plugins=[AttributePlugin()],
        dataset_plugins=[DatasetPlugin()],
        read_after=["quantities"],
        write_after=["quantities"]
    )]
