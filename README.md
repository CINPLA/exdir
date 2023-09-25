[![Project Status: Active - The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
[![codecov](https://codecov.io/gh/CINPLA/exdir/branch/dev/graph/badge.svg)](https://codecov.io/gh/CINPLA/exdir)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/CINPLA/exdir/dev?filepath=tests%2Fbenchmarks%2Fbenchmarks.ipynb)

*Important*: The reference implementation contained in this repository is intended for
feedback and as a basis for future library implementations.
It is not ready for production use.

# Experimental Directory Structure #

Experimental Directory Structure (exdir) is a proposed, open specification for
experimental pipelines.
Exdir is currently a prototype published to invite researchers to give feedback on
the standard.

Exdir is an hierarchical format based on open standards.
It is inspired by already existing formats, such as HDF5 and NumPy,
and attempts to solve some of the problems assosciated with these while
retaining their benefits.
The development of exdir owes a great deal to the efforts of others to standardize
data formats in science in general and neuroscience in particular, among them
the Klusta Kwik Team and Neurodata Without Borders.

## Installation

Exdir can be installed with Anaconda:

    conda install exdir -c cinpla -c conda-forge

## Usage

The following code creates an Exdir directory with a group and a dataset:

```
import numpy as np
import exdir

experiment = exdir.File("experiment.exdir")
group = experiment.create_group("group")
data = np.arange(10)
dataset = group.create_dataset("dataset", data=data)
```

The data can be retrieved using the above used keys:

```
group = experiment["group"]
dataset = group["dataset"]
print(dataset)
```

Attributes can be added to all objects, including files, groups and datasets:

```
group.attrs["room_number"] = 1234
dataset.attrs["recoring_date"] = "2018-02-04"
```

See the [documentation](https://exdir.readthedocs.io) for more information.

## Benchmarks ##

See [benchmarks.ipynb](tests/benchmarks/benchmarks.ipynb).

A [live version](https://mybinder.org/v2/gh/CINPLA/exdir/dev?filepath=tests%2Fbenchmarks%2Fbenchmarks.ipynb)
can be explored using Binder.

## Quick introduction ##

Exdir is not a file format in itself, but rather a standardized folder structure.
The abstract data model is almost equivalent to that of HDF5,
with groups, datasets, and attributes.
This was done to simplify the transition from either format.
However, data in Exdir is not stored in a single file,
but rather multiple files within the hierarchy.
The metadata is stored in a restricted verison of the YAML 1.2 format
and the binary data in the NumPy 2.0 format.

Here is an example structure:

```
example.exdir (File, folder)
│   attributes.yaml (-, file)
│   exdir.yaml (-, file)
│
├── dataset1 (Dataset, folder)
│   ├── data.npy (-, file)
│   ├── attributes.yaml (-, file)
│   └── exdir.yaml (-, file)
│
└── group1 (Group, folder)
│   ├── attributes.yaml (-, file)
    └── exdir.yaml (-, file)
    │
    ├── dataset3 (Dataset, folder)
    │   ├── data.npy (-, file)
    │   ├── attributes.yaml (-, file)
    │   └── exdir.yaml (-, file)
    │
    ├── link1 (Link, folder)
    │   └── exdir.yaml (-, file)
    │
    └── dataset4 (Dataset, folder)
        ├── data.npy (-, file)
        ├── attributes.yaml (-, file)
        ├── exdir.yaml (-, file)
        │
        └── raw (Raw, folder)
            ├── image0001.tif (-, file)
            ├── image0002.tif (-, file)
            └── ...
```

The above structure shows the name of the object, the type of the object in exdir and
the type of the object on the file system as follows:

```
[name] ([EXP type], [file system type])
```

A dash (-) indicates that the object doesn't have a separate internal
representation in the format, but is used indirectly.
It is however explicitly stored in the file system.

The above structure shows that the `example.exdir` file is simply a folder in
the file system, but when read by an exdir parser, it appears as a `File`.
The `File` is the root object of any structure.
The metadata of the `File` is stored in a file named meta.yaml.
This is internal to exdir.
Attributes of the `File` is stored in a file named attributes.yaml.
This is optional.

Below the file, multiple objects may appear, among them `Dataset`s and `Group`s.
Both `Dataset`s and `Group`s are stored as folders in the file system.
Both have their metadata stored in files named meta.yaml.
These are not visible as files within the exdir format, but appear simply as
the metadata for the `Dataset`s and `Group`s.

If there is any additional data assosciated with the dataset,
it may (optionally) be stored in a folder named `raw`.
This differs from HDF5, but allows storing raw data from experiments (such as
TIFF images from an external microscopy system) locally with the data
converted to the NumPy format.

## Goals and benefits ##

By reusing the structure of HDF5, exdir should be familiar to researchers that
have experience with this format.
However, by not storing the data in a single file,
the data is much less prone to corruption.
Further, HDF5 is not optimal for modifications, parallelization or data
exploration.

By storing the data in separate files, we get the many benefits of modern file
systems in protection against data corruption.
The data is more easily accessible in parallell computing and is stored in
a well known and tested format.
It is easier to explore the data by use of standard command line tools or simply
the file explorer.

However, we intend to develop a graphical user interface along the lines of
HDF5view that allows simple data exploration similar to this.

## Principles ##

- Exdir should be based on existing open standards
- Exdir should not solve problems that have already been solved, such as storing binary data
- Exdir should be lightweight

## Background ##

Exdir was designed due to a need at the Centre for Integrative
Neuroplasticity (CINPLA) at the University of Oslo for a format that would
fit the experimental pipeline.
While researching the different options, we found that the neuroscience
community had several formats for storing experimental data.
A large effort at standardizing the format in the community was spawned by
Neurodata Without Borders (NWB).
An initial version of the NWB format was published, based on the HDF5 format.
However, shortly after the first publication of NWB, concerns were voiced
about HDF5 format from the developers of the klusta project[1].
They had been using HDF5 as the underlying file format for their software suite
and started seeing problems with the file format among their users.
They saw multiple problems with HDF5 in the form of data corrpution, performance
issues, bugs and poor support for parallelization.

HDF5 is not optimal for modifications.
This is not a problem if you only store data from acquisition,
as this shouldn't be changed.
However, for analysis it is often necessary to modify the data multiple times as
different methods and parameters are tested.
At the same time, it is beneficial to keep the analysed data stored together
with the acquisition data.

[1] http://cyrille.rossant.net/moving-away-hdf5/
