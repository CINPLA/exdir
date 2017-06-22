import exdir
import pytest
import os
import shutil


def add_many_attributes(obj):
    for i in range(30):
        obj.attrs["hello" + str(i)] = "world"


def test_benchmark_attribute_many_exdir(benchmark, exdir_tmpfile):
    foo = exdir_tmpfile.create_group("foo")
    benchmark(add_many_attributes, foo)


def test_benchmark_attribute_many_h5py(benchmark, h5py_tmpfile):
    foo = h5py_tmpfile.create_group("foo")
    benchmark(add_many_attributes, foo)


def add_few_attributes(obj):
    for i in range(5):
        obj.attrs["hello" + str(i)] = "world"


def test_benchmark_attribute_few_exdir(benchmark, exdir_tmpfile):
    foo = exdir_tmpfile.create_group("foo")
    benchmark(add_few_attributes, foo)


def test_benchmark_attribute_few_h5py(benchmark, h5py_tmpfile):
    foo = h5py_tmpfile.create_group("foo")
    benchmark(add_few_attributes, foo)


def add_attribute_tree(obj):
    tree = {}
    for i in range(100):
        tree["hello" + str(i)] = "world"
    tree["intermediate"] = {}
    intermediate = tree["intermediate"]
    for level in range(10):
        level_str = "level" + str(level)
        intermediate[level_str] = {}
        intermediate = intermediate[level_str]
    intermediate = 42
    obj.attrs["test"] = tree


def test_benchmark_attribute_tree_exdir(benchmark, exdir_tmpfile):
    foo = exdir_tmpfile.create_group("foo")
    benchmark(add_attribute_tree, foo)


def test_benchmark_attribute_tree_h5py(benchmark, h5py_tmpfile):
    foo = h5py_tmpfile.create_group("foo")
    with pytest.raises(TypeError):
        benchmark(add_attribute_tree, foo)
