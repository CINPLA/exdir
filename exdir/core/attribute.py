from enum import Enum
import os
import numpy as np
import exdir
try:
    import ruamel_yaml as yaml
except ImportError:
    import ruamel.yaml as yaml

from .mode import assert_file_open, OpenMode, assert_file_writable

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
    """
    The attribute object is a dictionary-like object that is used to access
    the attributes stored in the :code:`attributes.yaml` file for a given
    Exdir Object.

    The Attribute object should not be created, but retrieved by accessing
    the :code:`.attrs` property of any Exdir Object, such as a Dataset,
    Group or File.
    """

    # TODO remove METADATA mode and read/write metadata directly as YAML instead
    class _Mode(Enum):
        ATTRIBUTES = 1
        METADATA = 2

    def __init__(self, parent, mode, file, path=None):
        self.parent = parent
        self.mode = mode
        self.file = file
        self.path = path or []

    def __getitem__(self, name=None):
        attrs = self._open_or_create()

        if self.mode == self._Mode.ATTRIBUTES:
            meta = self.parent.meta.to_dict()
            for plugin in self.file.plugin_manager.attribute_plugins.read_order:
                attribute_data = exdir.plugin_interface.AttributeData(
                    attrs=attrs,
                    meta=meta
                )

                attribute_data = plugin.prepare_read(attribute_data)
                attrs = attribute_data.attrs
                meta.update(attribute_data.meta)

        for i in self.path:
            attrs = attrs[i]
        if name is not None:
            attrs = attrs[name]
        if isinstance(attrs, dict):
            return Attribute(
                self.parent, self.mode, self.file, self.path + [name]
            )
        else:
            return attrs

    def __setitem__(self, name, value):
        attrs = self._open_or_create()
        key = name
        sub_attrs = attrs

        for i in self.path:
            sub_attrs = sub_attrs[i]
        sub_attrs[key] = value

        self._set_data(attrs)

    def __contains__(self, name):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return False
        attrs = self._open_or_create()
        for i in self.path:
            attrs = attrs[i]
        return name in attrs

    def keys(self):
        """
        Returns
        -------
        a new view of the Attribute's keys.
        """
        attrs = self._open_or_create()
        for i in self.path:
            attrs = attrs[i]
        return attrs.keys()

    def to_dict(self):
        """
        Convert the Attribute into a standard Python dictionary.
        """
        attrs = self._open_or_create()
        for i in self.path:  # TODO check if this is necesary
            attrs = attrs[i]

        if self.mode == self._Mode.ATTRIBUTES:
            meta = self.parent.meta.to_dict()
            attribute_data = exdir.plugin_interface.AttributeData(
                attrs=attrs,
                meta=meta
            )
            for plugin in self.file.plugin_manager.attribute_plugins.read_order:
                attribute_data = plugin.prepare_read(attribute_data)

                attrs = attribute_data.attrs

        return attrs

    def items(self):
        """
        Returns
        -------
        a new view of the Attribute's items.
        """
        attrs = self._open_or_create()
        for i in self.path:
            attrs = attrs[i]
        return attrs.items()

    def values(self):
        """
        Returns
        -------
        a new view of the Attribute's values.
        """
        attrs = self._open_or_create()
        for i in self.path:
            attrs = attrs[i]
        return attrs.values()

    def _set_data(self, attrs):
        assert_file_writable(self.file)
        plugins = self.file.plugin_manager.attribute_plugins.write_order

        if self.mode == self._Mode.ATTRIBUTES and len(plugins) > 0:
            meta = self.parent.meta.to_dict()
            for plugin in plugins:
                attribute_data = exdir.plugin_interface.AttributeData(
                    attrs=attrs,
                    meta=meta
                )

                attribute_data = plugin.prepare_write(attribute_data)
                meta = attribute_data.meta
                attrs = attribute_data.attrs

            attribute_data_quoted = _quote_strings(attribute_data.attrs)
            self.parent.meta._set_data(meta)
        else:
            attribute_data_quoted = attrs

        with self.filename.open("w", encoding="utf-8") as attribute_file:
            yaml.dump(
                attribute_data_quoted,
                attribute_file,
                default_flow_style=False,
                allow_unicode=True,
                Dumper=yaml.RoundTripDumper
            )

    # TODO only needs filename, make into free function
    def _open_or_create(self):
        assert_file_open(self.file)
        attrs = {}
        if self.filename.exists():  # NOTE str for Python 3.5 support
            with self.filename.open("r", encoding="utf-8") as meta_file:
                attrs = yaml.safe_load(meta_file)
        return attrs

    def __iter__(self):
        for key in self.keys():
            yield key

    @property
    def filename(self):
        """
        Returns
        -------
        The filename of the :code:`attributes.yaml` file.
        """
        assert_file_open(self.file)
        if self.mode == self._Mode.METADATA:
            return self.parent.meta_filename
        else:
            return self.parent.attributes_filename

    def __len__(self):
        return len(self.keys())

    def update(self, value):
        """
        Update the Attribute with the key/value pairs from :code:`value`, overwriting existing keys.

        This function accepts either another Attribute object, a dictionary object or an iterable of key/value pairs
        """
        for key in value:
            self[key] = value[key]

    def __str__(self):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return "<Attributes of closed Exdir object>"
        string = ""
        for key in self:
            string += "{}: {},".format(key, self[key])
        return "Attribute({}, {{{}}})".format(self.parent.name, string)

    def _repr_html_(self):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return False
        return exdir.utils.display.html_attrs(self)

    def __repr__(self):
        if self.file.io_mode == OpenMode.FILE_CLOSED:
            return "<Attributes of closed Exdir object>"
        return "Attributes of Exdir object '{}' at '{}'".format(
            self.parent.name, id(self))
