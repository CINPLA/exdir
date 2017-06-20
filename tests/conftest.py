import pytest
import shutil
import os

from exdir.core import File


def remove(name):
    if os.path.exists(name):
        shutil.rmtree(name)
    assert not os.path.exists(name)


@pytest.fixture
def setup_teardown_folder(tmpdir):
    testpath = tmpdir.mkdir("test")
    testdir = os.path.join(testpath, "exdir_dir")
    testfile = os.path.join(testpath, "test.exdir")

    remove(testpath)

    os.makedirs(testpath)

    yield testpath, testfile, testdir

    remove(testpath)


@pytest.fixture
def setup_teardown_file(tmpdir):
    testpath = tmpdir.mkdir("test")
    testdir = os.path.join(testpath, "exdir_dir")
    testfile = os.path.join(testpath, "test.exdir")

    remove(testpath)

    os.makedirs(testpath)

    f = File(testfile, mode="w")

    yield testpath, testfile, testdir, f

    f.close()

    remove(testpath)
