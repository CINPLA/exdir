import pytest
import shutil
import os

from exdir.core import File


filepath = os.path.abspath(__file__)
filedir = os.path.dirname(filepath)

testmaindir = ".expipe_test_dir_Aegoh4ahlaechohV5ooG9vew1yahDe2d"
TESTPATH = os.path.join(filedir, testmaindir)
TESTDIR = os.path.join(TESTPATH, "exdir_dir")
TESTFILE = os.path.join(TESTPATH, "test.exdir")


def pytest_namespace():
    return {"TESTPATH": TESTPATH,
            "TESTDIR": TESTDIR,
            "TESTFILE": TESTFILE}


def remove(name):
    if os.path.exists(name):
        shutil.rmtree(name)
    assert(not os.path.exists(name))


@pytest.fixture
def setup_teardown_folder():
    remove(TESTPATH)

    os.makedirs(TESTPATH)

    yield

    remove(TESTPATH)


@pytest.fixture
def setup_teardown_file():
    remove(TESTPATH)

    os.makedirs(TESTPATH)

    f = File(TESTFILE, mode="w")

    yield f

    f.close()

    remove(TESTPATH)
