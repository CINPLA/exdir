import exdir
import pytest
import os
import shutil
import h5py
import numpy as np


def add_small_dataset(obj):
    data = np.zeros((100, 100, 100))
    obj.create_dataset("foo", data=data)
    obj.close()


def add_medium_dataset(obj):
    data = np.zeros((1000, 100, 100))
    obj.create_dataset("foo", data=data)
    obj.close()


def add_large_dataset(obj):
    data = np.zeros((1000, 1000, 100))
    obj.create_dataset("foo", data=data)
    obj.close()


def create_setup_h5py(tmpdir):
    def setup():
        testpath = str(tmpdir.mkdir("test").join("test.h5"))
        if os.path.exists(testpath):
            os.remove(testpath)
        f = h5py.File(testpath)
        return ((f,), {})
    return setup


def test_dataset_small_h5py(benchmark, tmpdir):
    benchmark.pedantic(add_small_dataset, setup=create_setup_h5py(tmpdir))


def test_dataset_medium_h5py(benchmark, tmpdir):
    benchmark.pedantic(add_medium_dataset, setup=create_setup_h5py(tmpdir))


def test_dataset_large_h5py(benchmark, tmpdir):
    benchmark.pedantic(add_large_dataset, setup=create_setup_h5py(tmpdir))


def create_setup_exdir(tmpdir):
    def setup():
        testpath = str(tmpdir.mkdir("test").join("test.exdir"))
        if os.path.exists(testpath):
            shutil.rmtree(testpath)
        f = exdir.File(testpath)
        return ((f,), {})
    return setup


def test_dataset_small_exdir(benchmark, tmpdir):
    benchmark.pedantic(add_small_dataset, setup=create_setup_exdir(tmpdir))


def test_dataset_medium_exdir(benchmark, tmpdir):
    benchmark.pedantic(add_medium_dataset, setup=create_setup_exdir(tmpdir))


def test_dataset_large_exdir(benchmark, tmpdir):
    benchmark.pedantic(add_large_dataset, setup=create_setup_exdir(tmpdir))
