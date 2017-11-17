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
        def prepare_read(self, values, attrs):
            return values

        def prepare_write(self, data):
            return data, {}, {}

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
        def prepare_read(self, values, attrs):
            return values

        def prepare_write(self, data):
            plugin_meta = {}
            attrs = {}
            return data, attrs, plugin_meta

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
        def prepare_read(self, values, attrs):
            return values

        def prepare_write(self, data):
            plugin_meta = {
                "required": True
            }
            attrs = {}
            return data, attrs, plugin_meta

    required = exdir.plugin_interface.Plugin(
        "required",
        dataset_plugins=[DatasetPlugin()]
    )

    f = exdir.File(setup_teardown_folder[1], 'w', plugins=required)
    assert f
    d = f.create_dataset("foo", data=np.array([1, 2, 3]))
    assert all(d.data == np.array([1, 2, 3]))
    f.close()

    f = exdir.File(setup_teardown_folder[1], 'r+')
    assert f
    d = f["foo"]
    with pytest.raises(Exception):
        print(d.data)
    f.close()


def test_one_way_scaling(setup_teardown_folder):
    class DatasetPlugin(exdir.plugin_interface.Dataset):
        def prepare_read(self, values, attrs):
            return values

        def prepare_write(self, data):
            plugin_meta = {
                "required": False
            }
            attrs = {}
            return data * 2, attrs, plugin_meta

    one_way_scaling = exdir.plugin_interface.Plugin(
        "one_way_scaling",
        dataset_plugins=[DatasetPlugin()]
    )

    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[one_way_scaling])
    assert f
    d = f.create_dataset("foo", data=np.array([1, 2, 3]))
    assert all(d.data == np.array([2, 4, 6]))
    f.close()


def test_scaling(setup_teardown_folder):

    class DatasetPlugin(exdir.plugin_interface.Dataset):
        def prepare_read(self, values, attrs):
            return values / 2

        def prepare_write(self, data):
            plugin_meta = {
                "required": True
            }
            attrs = {}
            return data * 2, attrs, plugin_meta

    scaling = exdir.plugin_interface.Plugin(
        "scaling",
        dataset_plugins=[DatasetPlugin()]
    )

    f = exdir.File(setup_teardown_folder[1], 'w', plugins=[scaling])
    assert f
    d = f.create_dataset("foo", data=np.array([1, 2, 3]))
    assert all(d.data == np.array([1, 2, 3]))
    f.close()
