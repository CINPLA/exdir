import pytest
import shutil
import os
import h5py
import pathlib

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
