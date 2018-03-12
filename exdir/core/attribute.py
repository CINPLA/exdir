from enum import Enum
import ruamel_yaml as yaml
import os
import numpy as np
import exdir

from . import exdir_object as exob


def _quote_strings(value):
    if isinstance(value, str):
        return yaml.scalarstring.DoubleQuotedScalarString(value)
    else:
        try:
            new_result = {}
            for key, val in value.items():
                new_result[key] = _quote_strings(val)
            return new_result
        except AttributeError:
            pass
    return value


class Attribute(object):
    """Attribute class."""

    class Mode(Enum):
        ATTRIBUTES = 1
        METADATA = 2

    def __init__(self, parent, mode, io_mode, path=None, plugin_manager=None):
        self.parent = parent
        self.mode = mode
        self.io_mode = io_mode
        self.path = path or []
        self.plugin_manager = plugin_manager

    def __getitem__(self, name=None):
        meta_data = self._open_or_create()

        for plugin in self.plugin_manager.attribute_plugins.read_order:
            meta_data = plugin.prepare_read(meta_data)

        for i in self.path:
            meta_data = meta_data[i]
        if name is not None:
            meta_data = meta_data[name]
        if isinstance(meta_data, dict):
            return Attribute(
                self.parent, self.mode, self.io_mode, self.path + [name],
                plugin_manager=self.plugin_manager
            )
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

        for plugin in self.plugin_manager.attribute_plugins.read_order:
            meta_data = plugin.prepare_read(meta_data)

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

        for plugin in self.plugin_manager.attribute_plugins.write_order:
            meta_data = plugin.prepare_write(meta_data)

        meta_data_quoted = _quote_strings(meta_data)

        with self.filename.open("w", encoding="utf-8") as meta_file:
            yaml.dump(
                meta_data_quoted,
                meta_file,
                default_flow_style=False,
                allow_unicode=True,
                Dumper=yaml.RoundTripDumper
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
