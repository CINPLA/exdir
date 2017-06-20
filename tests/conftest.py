import pytest
import shutil
import os

import exdir


def remove(name):
    if os.path.exists(name):
        shutil.rmtree(name)
    assert not os.path.exists(name)


@pytest.fixture
def setup_teardown_folder(tmpdir):
    testpath = str(tmpdir.mkdir("test"))
    testdir = os.path.join(testpath, "exdir_dir")
    testfile = os.path.join(testpath, "test.exdir")

    remove(testpath)

    os.makedirs(testpath)

    yield testpath, testfile, testdir

    remove(testpath)


@pytest.fixture
def setup_teardown_file(tmpdir):
    testpath = str(tmpdir.mkdir("test"))
    testdir = os.path.join(testpath, "exdir_dir")
    testfile = os.path.join(testpath, "test.exdir")

    remove(testpath)

    os.makedirs(testpath)

    f = exdir.File(testfile, mode="w")

    yield testpath, testfile, testdir, f

    f.close()

    remove(testpath)

@pytest.fixture
def exdir_tmpfile(tmpdir):
    testpath = str(tmpdir.mkdir("test").join("test.exdir"))
    f = exdir.File(testpath, mode="w")
    yield f
    f.close()
    remove(testpath)


@pytest.fixture
def h5py_tmpfile(tmpdir):
    import h5py
    testpath = str(tmpdir.mkdir("test").join("test.h5"))
    f = h5py.File(testpath, mode="w")
    yield f
    f.close()
    os.remove(testpath)
