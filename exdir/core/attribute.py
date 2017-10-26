from enum import Enum
import yaml
import os
import numpy as np
import exdir

import quantities as pq

from . import exdir_object as exob


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

class Attribute(object):
    """Attribute class."""

    class Mode(Enum):
        ATTRIBUTES = 1
        METADATA = 2

    def __init__(self, parent, mode, io_mode, path=None):
        self.parent = parent
        self.mode = mode
        self.io_mode = io_mode
        self.path = path or []

    def __getitem__(self, name=None):
        meta_data = self._open_or_create()

        for plugin in exdir.attribute_plugins:
            meta_data = plugin.preprocess_meta_data(self, meta_data)

        for i in self.path:
            meta_data = meta_data[i]
        if name is not None:
            meta_data = meta_data[name]
        if isinstance(meta_data, dict):
            return Attribute(self.parent, self.mode, self.io_mode,
                             self.path + [name])
        else:
            return meta_data

    def __setitem__(self, name, value):
        meta_data = self._open_or_create()

        # if isinstance(name, np.integer):
        #     key = int(name)
        # else:
        #     key = name
        key = name

        sub_meta_data = meta_data
        for i in self.path:
            sub_meta_data = sub_meta_data[i]
        sub_meta_data[key] = value

        self._set_data(meta_data)

    def __contains__(self, name):
        meta_data = self._open_or_create()
        for i in self.path:
            meta_data = meta_data[i]
        return name in meta_data

    def keys(self):
        meta_data = self._open_or_create()
        for i in self.path:
            meta_data = meta_data[i]
        return meta_data.keys()

    def to_dict(self):
        meta_data = self._open_or_create()
        for i in self.path:  # TODO check if this is necesary
            meta_data = meta_data[i]
        meta_data = convert_back_quantities(meta_data)
        return meta_data

    def items(self):
        meta_data = self._open_or_create()
        for i in self.path:
            meta_data = meta_data[i]
        return meta_data.items()

    def values(self):
        meta_data = self._open_or_create()
        for i in self.path:
            meta_data = meta_data[i]
        return meta_data.values()

    def _set_data(self, meta_data):
        if self.io_mode == exob.Object.OpenMode.READ_ONLY:
            raise IOError("Cannot write in read only ("r") mode")
        meta_data = convert_quantities(meta_data)
        with self.filename.open("w", encoding="utf-8") as meta_file:
            yaml.safe_dump(
                meta_data,
                meta_file,
                default_flow_style=False,
                allow_unicode=True
            )

    # TODO only needs filename, make into free function
    def _open_or_create(self):
        meta_data = {}
        if self.filename.exists():  # NOTE str for Python 3.5 support
            with self.filename.open("r", encoding="utf-8") as meta_file:
                meta_data = yaml.safe_load(meta_file)
        return meta_data

    def __iter__(self):
        for key in self.keys():
            yield key

    @property
    def filename(self):
        if self.mode == self.Mode.METADATA:
            return self.parent.meta_filename
        else:
            return self.parent.attributes_filename

    def __len__(self):
        return len(self.keys())

    def update(self, value):
        for key in value:
            self[key] = value[key]

    def __str__(self):
        string = ""
        for key in self:
            string += "{}: {},".format(key, self[key])
        return "Attribute({}, {{{}}})".format(self.parent.name, string)
