import exdir
import quantities as pq
import numpy as np


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
    def prepare_write(self, meta_data):
        result = convert_to_list(meta_data)
        return result

    def prepare_read(self, meta_data):
        return convert_from_list(meta_data)


def plugins():
    return [exdir.plugin_interface.Plugin(
        "numpy_attributes",
        attribute_plugins=[AttributePlugin()],
        read_after=["quantities"],
        write_after=["quantities"]
    )]
