import exdir
import numpy as np
import quantities as pq
exdir_file = exdir.File("/tmp/test.exdir")
attrs = exdir_file.attrs
print(attrs)
print(attrs["lol"])
print(attrs["test"])

attrs["test"] = 14
attrs["lol"]["blah"] = 14

attrs["hehe"] = {
    "my": "value",
    "is": "awesome"
}

group = exdir_file.require_group("test")
group.attrs = {"test": np.array([0, 1, 2, 3])}
# attrs["lol"] = 23
# attrs["blah"] = 42 * pq.s
# exdir_file.attrs = attrs
