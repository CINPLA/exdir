import exdir
import pytest
import os
import shutil
import timeit
import h5py
import time
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

def create_setup_exdir(tmpdir):
    def setup():
        testpath = "/home/svenni/tmp/ramdisk/test.exdir"
        # testpath = tmpdir / "test.exdir"
        if os.path.exists(testpath):
            shutil.rmtree(testpath)
        f = exdir.File(testpath)
        return f, testpath
    return setup

def create_setup_h5py(tmpdir):
    def setup():
        testpath = "/home/svenni/tmp/ramdisk/test.h5"
        # testpath = tmpdir / "test.h5"
        if os.path.exists(testpath):
            os.remove(testpath)
        f = h5py.File(testpath)
        return f, testpath
    return setup

def teardown_exdir(f, testpath):
    f.close()
    shutil.rmtree(testpath)

def teardown_h5py(f, testpath):
    os.remove(testpath)

def test_benchmark_exdir_small(tmpdir, exdir_benchmark):
    def target(f, testpath):
        add_small_dataset(f)
    exdir_benchmark("exdir_small", target, create_setup_exdir(tmpdir), teardown_exdir, iterations=100)

def test_benchmark_h5py_small(tmpdir, exdir_benchmark):
    def target(f, testpath):
        add_small_dataset(f)
    exdir_benchmark("h5py_small", target, create_setup_h5py(tmpdir), teardown_h5py, iterations=100)

def test_benchmark_exdir_large(tmpdir, exdir_benchmark):
    def target(f, testpath):
        add_large_dataset(f)
    exdir_benchmark("exdir_large", target, create_setup_exdir(tmpdir), teardown_exdir, iterations=10)

def test_benchmark_h5py_large(tmpdir, exdir_benchmark):
    def target(f, testpath):
        add_large_dataset(f)
    exdir_benchmark("h5py_large", target, create_setup_h5py(tmpdir), teardown_h5py, iterations=10)


# def test_dataset_small_exdir(benchmark, tmpdir):
#     benchmark.pedantic(add_small_dataset, setup=create_setup_exdir(tmpdir))
#
#
# def test_dataset_medium_exdir(benchmark, tmpdir):
#     benchmark.pedantic(add_medium_dataset, setup=create_setup_exdir(tmpdir))
#
#
# def test_dataset_large_exdir(benchmark, tmpdir):
#     benchmark.pedantic(add_large_dataset, setup=create_setup_exdir(tmpdir))
