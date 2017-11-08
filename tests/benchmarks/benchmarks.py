import exdir
import pytest
import os
import shutil
import time
import numpy as np
import h5py

def benchmark(name, target, setup=None, teardown=None, iterations=1):
    total_time = 0
    setup_teardown_start = time.time()
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
    setup_teardown_end = time.time()
    total_setup_teardown = setup_teardown_end - setup_teardown_start

    output = (
        "{name}\n" +
        ("-" * len(name)) + "\n" +
        "Iterations:\n{iterations}\n" +
        "Total time:\n{total_time}\n" +
        "Total time (iterations + setup/teardown):\n{total_setup_teardown}\n" +
        "Mean:\n{mean}\n"
    ).format(
        name=name,
        iterations=iterations,
        total_time=total_time,
        total_setup_teardown=total_setup_teardown,
        mean=total_time / iterations
    )

    print(output)


def setup_exdir():
    testpath = "/tmp/ramdisk/test.exdir"
    # testpath = tmpdir / "test.exdir"
    if os.path.exists(testpath):
        shutil.rmtree(testpath)
    f = exdir.File(testpath)
    return f, testpath


def setup_h5py():
    testpath = "/tmp/ramdisk/test.h5"
    # testpath = tmpdir / "test.h5"
    if os.path.exists(testpath):
        os.remove(testpath)
    f = h5py.File(testpath)
    return f, testpath


def benchmark_exdir(function, iterations=100):
    benchmark(
        "exdir_" + function.__name__,
        lambda f, tmpdir: function(f),
        setup_exdir,
        teardown_exdir,
        iterations=iterations
    )


def benchmark_h5py(function, iterations=100):
    benchmark(
        "h5py_" + function.__name__,
        lambda f, tmpdir: function(f),
        setup_h5py,
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
    for i in range(100):
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
    for i in range(5000):
        group = obj.create_group("group{}".format(i))
        # data = np.zeros((10, 10, 10))
        # group.create_dataset("dataset{}".format(i), data=data)


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


if not os.path.exists("/tmp/ramdisk"):
    print("Error: You need to set up a ramdisk at /tmp/ramdisk first:")
    print()
    print("    mkdir /tmp/ramdisk/")
    print("    sudo mount -t tmpfs -o size=2048M tmpfs /tmp/ramdisk/")
    print()
    print("Rerun this script after setting up the ramdisk.")

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

def create_setup_many_objects(setup_function):
    def setup():
        obj, path = setup_function()
        create_many_objects(obj)
        return obj, path
    return setup

benchmark(
    "exdir_iteration",
    lambda obj, path: iterate_objects(obj),
    create_setup_many_objects(setup_exdir),
    teardown_exdir,
    iterations=2
)

benchmark(
    "h5py_iteration",
    lambda obj, path: iterate_objects(obj),
    create_setup_many_objects(setup_h5py),
    teardown_h5py,
    iterations=2
)

def partial_write(dataset):
    dataset[320:420, 0:100, 0:100] = np.ones((100, 100, 100))

def create_setup_dataset(setup_function):
    def setup():
        f, path = setup_function()
        data = np.zeros((1000, 100, 100))
        dataset = f.create_dataset("foo", data=data)
        return dataset, f, path
    return setup

benchmark(
    "exdir_partial",
    lambda dataset, f, path: partial_write(dataset),
    create_setup_dataset(setup_exdir),
    lambda dataset, f, path: teardown_exdir(f, path),
    iterations=200
)

benchmark(
    "h5py_partial",
    lambda dataset, f, path: partial_write(dataset),
    create_setup_dataset(setup_h5py),
    lambda dataset, f, path: teardown_h5py(f, path),
    iterations=200
)
