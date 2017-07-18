# This is a usecase that shows how h5py can be swapped with exdir.
# usecase_h5py.py shows the same usecase with h5py instead

import exdir
import numpy as np

time = np.linspace(0, 100, 101)

voltage_1 = np.sin(time)
voltage_2 = np.sin(time) + 10


f = exdir.File("experiments.exdir", "w")
f.attrs['description'] = "This is a mock experiment with voltage values over time"


# Creating group and datasets for experiment 1
grp_1 = f.create_group("experiment_1")

dset_time_1 = grp_1.create_dataset("time", data=time)
dset_time_1.attrs['unit'] = "ms"

dset_voltage_1 = grp_1.create_dataset("voltage", data=voltage_1)
dset_voltage_1.attrs['unit'] = "mV"


# Creating group and datasets for experiment 2
grp_2 = f.create_group("experiment_2")

dset_time_2 = grp_2.create_dataset("time", data=time)
dset_time_2.attrs['unit'] = "ms"

dset_voltage_2 = grp_2.create_dataset("voltage", data=voltage_2)
dset_voltage_2.attrs['unit'] = "mV"


# Creating group and subgroup for experiment 3
grp_3 = f.create_group("experiment_invalid")



# Looping through and accessing
print("Experiments: ", list(f.keys()))
for experiment in f.keys():
    if "voltage" in f[experiment]:
        print(experiment)
        print(f[experiment]["voltage"])
        print("First voltage:", f[experiment]["voltage"][0])
    else:
        print("No voltage values for: {}".format(experiment))




# Creating and accessing a subgroup
grp_4 = grp_3.create_group("subgroup")
dset_time_4 = grp_4.create_dataset("time", data=time)

print(f["experiment_invalid"]["subgroup"]["time"])

f.close()


import exdir