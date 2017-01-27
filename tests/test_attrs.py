import exdir
import quantities as pq
exdir_file = exdir.File("/tmp/test.exdir")
attrs = exdir_file.attrs
print(attrs)
attrs["lol"] = 23
attrs["blah"] = 24 * pq.s
exdir_file.attrs = attrs
