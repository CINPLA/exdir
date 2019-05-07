from __future__ import print_function

import pytest
import shutil
import os
import h5py
try:
    import pathlib
except ImportError as e:
    try:
        import pathlib2 as pathlib
    except ImportError:
        raise e
import time

import exdir


def remove(name):
    if name.exists():
        shutil.rmtree(str(name))
    assert not name.exists()


@pytest.fixture
def setup_teardown_folder(tmpdir):
    testpath = pathlib.Path(tmpdir.strpath)
    testdir = testpath / "exdir_dir"
    testfile = testpath / "test.exdir"

    remove(testpath)

    testpath.mkdir(parents=True)

    yield testpath, testfile, testdir

    remove(testpath)


@pytest.fixture
def setup_teardown_file(tmpdir):
    testpath = pathlib.Path(tmpdir.strpath)
    testdir = testpath / "exdir_dir"
    testfile = testpath / "test.exdir"

    remove(testpath)

    testpath.mkdir(parents=True)

    f = exdir.File(testfile, mode="w")

    yield testpath, testfile, testdir, f

    f.close()

    remove(testpath)

@pytest.fixture
def exdir_tmpfile(tmpdir):
    testpath = pathlib.Path(tmpdir.strpath) / "test.exdir"
    f = exdir.File(testpath, mode="w")
    yield f
    f.close()
    remove(testpath)


@pytest.fixture
def h5py_tmpfile(tmpdir):
    testpath = pathlib.Path(tmpdir.strpath) / "test.h5"
    f = h5py.File(testpath, mode="w")
    yield f
    f.close()
    os.remove(str(testpath))


@pytest.fixture
def quantities_tmpfile(tmpdir):
    testpath = pathlib.Path(tmpdir.strpath) / "test.exdir"
    f = exdir.File(testpath, mode="w", plugins=exdir.plugins.quantities)
    yield f
    f.close()
    remove(testpath)

@pytest.fixture
def exdir_benchmark(tmpdir):
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
        print("Mean:", total_time / iterations, sep="\n")
        print("--------------------")

    yield benchmark
