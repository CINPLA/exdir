# -*- coding: utf-8 -*-
#
# This file is part of Exdir, the Experimental Directory Structure.
#
# Copyright 2017 Svenn-Arne Dragly
# Copyright 2017 Simen Tennøe
#
# License: MIT, see "LICENSE" file for the full license terms.
#
# This file contains code from h5py, a Python interface to the HDF5 library,
# licensed under a standard 3-clause BSD license
# with copyright Andrew Collette and contributors.
# See http://www.h5py.org and the "3rdparty/h5py-LICENSE" file for details.


import pytest
import numpy as np
import os
import quantities as pq

import exdir
import exdir.core


def test_plugin_order():
    class DatasetPlugin(exdir.plugin_interface.Dataset):
        def prepare_read(self, dataset_data):
            return values

        def prepare_write(self, dataset_data):
            return dataset_data

    first = exdir.plugin_interface.Plugin(
        "first",
        write_before=["third"],
        read_before=["second"],
        dataset_plugins=[DatasetPlugin()]
    )

    second = exdir.plugin_interface.Plugin(
        "second",
        write_after=["first", "dummy"],
        read_after=["first", "none"],
        read_before=["third", "dummy"],
        dataset_plugins=[DatasetPlugin()]
    )

    third = exdir.plugin_interface.Plugin(
        "third",
        write_after=["second", "test"],
        write_before=["fourth", "test"],
        read_after=["first", "test"],
        read_before=["fourth", "test"],
        dataset_plugins=[DatasetPlugin()]
    )

    fourth = exdir.plugin_interface.Plugin(
        "fourth",
        write_before=["fifth", "test"],
        read_before=["fifth", "something"],
        dataset_plugins=[DatasetPlugin()]
    )

    fifth = exdir.plugin_interface.Plugin(
        "fifth",
        write_after=["first", "second", "third"],
        read_after=["third", "dummy"],
        dataset_plugins=[DatasetPlugin()]
    )

    manager = exdir.plugin_interface.plugin_interface.Manager([first, second, third, fourth, fifth])

    names = [plugin._plugin_module.name for plugin in manager.dataset_plugins.write_order]
    assert(names == ["first", "second", "third", "fourth", "fifth"])
    names = [plugin._plugin_module.name for plugin in manager.dataset_plugins.read_order]
    assert(names == ["first", "second", "third", "fourth", "fifth"])


def test_noop(setup_teardown_folder):
    class DatasetPlugin(exdir.plugin_interface.Dataset):
        def prepare_read(self, dataset_data):
            return dataset_data

        def prepare_write(self, dataset_data):
            return dataset_data

    noop = exdir.plugin_interface.Plugin(
        "noop",
        dataset_plugins=[DatasetPlugin()]
    )

    f = exdir.File(setup_teardown_folder[1], 'w', plugins=noop)
    d = f.create_dataset("foo", data=np.array([1, 2, 3]))
    assert all(d.data == np.array([1, 2, 3]))
    f.close()


def test_fail_reading_without_required(setup_teardown_folder):
    class DatasetPlugin(exdir.plugin_interface.Dataset):
        def prepare_read(self, dataset_data):
            return dataset_data

        def prepare_write(self, dataset_data):
            if "plugins" not in dataset_data.meta:
                dataset_data.meta["plugins"] = {}
            if "required" not in dataset_data.meta["plugins"]:
                dataset_data.meta["plugins"]["required"] = {"required": True}
            return dataset_data

    required = exdir.plugin_interface.Plugin(
        "required",
        dataset_plugins=[DatasetPlugin()]
    )

    f = exdir.File(setup_teardown_folder[1], 'w', plugins=required)
    assert isinstance(f, exdir.File)
    d = f.create_dataset("foo", data=np.array([1, 2, 3]))
    assert all(d.data == np.array([1, 2, 3]))
    f.close()

    f = exdir.File(setup_teardown_folder[1], 'r+')
    assert isinstance(f, exdir.File)
    d = f["foo"]
    with pytest.raises(Exception):
        print(d.data)
    f.close()


def test_one_way_scaling(setup_teardown_folder):
    class DatasetPlugin(exdir.plugin_interface.Dataset):
        def prepare_read(self, dataset_data):
            return dataset_data

        def prepare_write(self, dataset_data):
            if "plugins" not in dataset_data.meta:
                dataset_data.meta["plugins"] = {}
            if "scaling" not in dataset_data.meta["plugins"]:
                dataset_data.meta["plugins"]["scaling"] = {"required": True}
            dataset_data.data *= 2
            return dataset_data

    one_way_scaling = exdir.plugin_interface.Plugin(
        "scaling",
        dataset_plugins=[DatasetPlugin()]
    )

    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[one_way_scaling])
    assert isinstance(f, exdir.File)
    d = f.create_dataset("scaling", data=np.array([1, 2, 3]))
    assert all(d.data == np.array([2, 4, 6]))
    f.close()


def test_scaling(setup_teardown_folder):

    class DatasetPlugin(exdir.plugin_interface.Dataset):
        def prepare_read(self, dataset_data):
            meta = dataset_data.meta
            dataset_data.data = dataset_data.data / 2
            return dataset_data

        def prepare_write(self, dataset_data):
            dataset_data.data *= 2
            if "plugins" not in dataset_data.meta:
                dataset_data.meta["plugins"] = {}
            if "scaling" not in dataset_data.meta["plugins"]:
                dataset_data.meta["plugins"]["scaling"] = {"required": True}
            dataset_data.meta
            return dataset_data

    scaling = exdir.plugin_interface.Plugin(
        "scaling",
        dataset_plugins=[DatasetPlugin()]
    )

    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[scaling])
    assert isinstance(f, exdir.File)
    d = f.create_dataset("scaling", data=np.array([1, 2, 3]))
    assert all(d.data == np.array([1, 2, 3]))
    f.close()


def test_attribute_plugin(setup_teardown_folder):
    class AttributePlugin(exdir.plugin_interface.Attribute):
        def prepare_read(self, attribute_data):
            attribute_data.attrs["value"] = attribute_data.attrs["value"]["value"]
            return attribute_data

        def prepare_write(self, attribute_data):
            meta = attribute_data.meta
            if "plugins" not in meta:
                meta["plugins"] = {}
            if "scaling" not in meta["plugins"]:
                meta["plugins"]["scaling"] = {"required": True}
            old_value = attribute_data.attrs["value"]
            attribute_data.attrs["value"] = {
                "unit": "m",
                "value": old_value * 2
            }
            return attribute_data

    scaling_unit = exdir.plugin_interface.Plugin(
        "scaling",
        attribute_plugins=[AttributePlugin()]
    )

    f = exdir.File(setup_teardown_folder[1], "w", plugins=[scaling_unit])
    assert isinstance(f, exdir.File)
    d = f.create_dataset("foo", data=np.array([1, 2, 3]))
    d.attrs["value"] = 42
    assert d.attrs["value"] == 84
    f.close()

def test_reading_in_order(setup_teardown_folder):
    class DatasetPlugin1(exdir.plugin_interface.Dataset):
        def prepare_read(self, dataset_data):
            dataset_data.data = dataset_data.data * 2
            return dataset_data

    class DatasetPlugin2(exdir.plugin_interface.Dataset):
        def prepare_read(self, dataset_data):
            dataset_data.data = dataset_data.data * 3
            return dataset_data

    plugin1 = exdir.plugin_interface.Plugin(
        "plugin1",
        dataset_plugins=[DatasetPlugin1()]
    )
    plugin2 = exdir.plugin_interface.Plugin(
        "plugin2",
        dataset_plugins=[DatasetPlugin2()]
    )

    f = exdir.File(setup_teardown_folder[1], "w", plugins=[plugin1, plugin2])
    assert isinstance(f, exdir.File)
    d = f.create_dataset("foo", data=np.array([1, 2, 3]))
    assert all(d.data == np.array([6, 12, 18]))
    f.close()
