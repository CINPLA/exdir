import exdir
import exdir.core.filename_validation
import pytest
import os
import shutil
import time
import numpy as np
import h5py

def setup_exdir():
    testpath = "/tmp/ramdisk/test.exdir"
    # testpath = tmpdir / "test.exdir"
    if os.path.exists(testpath):
        shutil.rmtree(testpath)
    f = exdir.File(testpath, validate_name=exdir.core.filename_validation.none)
    return f, testpath

obj = setup_exdir()[0]

for i in range(5000):
    group = obj.create_group("group{}".format(i))
