import exdir
import pytest
import os
import shutil
import time
import numpy as np
import h5py

def benchmark(name, target, setup=None, teardown=None, iterations=1):
    total_time = 0
    for i in range(iterations):
        data = tuple()
        if setup is not None:
            data = setup()
        start_time = time.time()
        target(*data)
        end_time = time.time()
        total_time += end_time - start_time
        if teardown is not None:
            teardown(*data)
    print("--------------------")
    print("Result for:", name, sep="\n")
    print("Iterations:", iterations, sep="\n")
    print("Total:", total_time, sep="\n")
    print("Mean:", total_time / iterations, sep="\n")
    print("--------------------")


def create_setup_exdir():
    def setup():
        testpath = "/home/svenni/tmp/ramdisk/test.exdir"
        # testpath = tmpdir / "test.exdir"
        if os.path.exists(testpath):
            shutil.rmtree(testpath)
        f = exdir.File(testpath)
        return f, testpath
    return setup


def create_setup_h5py():
    def setup():
        testpath = "/home/svenni/tmp/ramdisk/test.h5"
        # testpath = tmpdir / "test.h5"
        if os.path.exists(testpath):
            os.remove(testpath)
        f = h5py.File(testpath)
        return f, testpath
    return setup


def benchmark_exdir(function, iterations=100):
    benchmark(
        "exdir_" + function.__name__,
        lambda f, tmpdir: function(f),
        create_setup_exdir(),
        teardown_exdir,
        iterations=iterations
    )


def benchmark_h5py(function, iterations=100):
    benchmark(
        "h5py_" + function.__name__,
        lambda f, tmpdir: function(f),
        create_setup_h5py(),
        teardown_h5py,
        iterations=iterations
    )


def teardown_exdir(f, testpath):
    f.close()
    shutil.rmtree(testpath)


def teardown_h5py(f, testpath):
    os.remove(testpath)


def add_few_attributes(obj):
    for i in range(5):
        obj.attrs["hello" + str(i)] = "world"


def add_many_attributes(obj):
    for i in range(30):
        obj.attrs["hello" + str(i)] = "world"


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


def create_many_objects(obj):
    for i in range(500):
        group = obj.create_group("group{}".format(i))
        data = np.zeros((10, 10, 10))
        group.create_dataset("dataset{}".format(i), data=data)


def iterate_objects(obj):
    i = 0
    for a in obj:
        i += 1
    return i


def create_large_tree(obj, level=0):
    if level > 4:
        return
    for i in range(3):
        group = obj.create_group("group_{}_{}".format(i, level))
        data = np.zeros((10, 10, 10))
        group.create_dataset("dataset_{}_{}".format(i, level), data=data)
        create_large_tree(group, level + 1)


def test_benchmark_attributes(exdir_benchmark):
    benchmarks = [
        (add_few_attributes, 100),
        (add_many_attributes, 10),
        #(add_attribute_tree, 100),
        (add_small_dataset, 100),
        (add_medium_dataset, 10),
        (add_large_dataset, 10),
        (create_many_objects, 3),
        (create_large_tree, 10),
    ]

    for function, iterations in benchmarks:
        benchmark_exdir(function, iterations)
        benchmark_h5py(function, iterations)

    benchmark_exdir(add_attribute_tree)


def test_benchmark_iteration():
    def setup_exdir():
        obj, path = create_setup_exdir()()
        create_many_objects(obj)
        return obj, path

    def setup_h5py():
        obj, path = create_setup_h5py()()
        create_many_objects(obj)
        return obj, path

    benchmark(
        "exdir_iteration",
        lambda obj, path: iterate_objects(obj),
        setup_exdir,
        teardown_exdir,
        iterations=2
    )

    benchmark(
        "h5py_iteration",
        lambda obj, path: iterate_objects(obj),
        setup_h5py,
        teardown_h5py,
        iterations=2
    )
