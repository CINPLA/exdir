*Important*: The implementations contained in this repository are intended for
feedback and as a basis for future reference implementations.
They are not ready for production use.

# Experimental Directory Structure #

The Experimental Directory Structure (exdir) is a proposed, open file format standard for
experimental pipelines.
exdir is currently a prototype published to invite researchers to give feedback on
the standard.

exdir is an hierarchical format based on open standards.
It is inspired by already existing formats, such as HDF5 and NumPy,
and attempts to solve some of the problems assosciated with these while
retaining their benefits.
The development of exdir owes a great deal to the efforts of others to standardize
data formats in science in general and neuroscience in particular, among them 
the Klusta Kwik Team and Neuroscience Without Borders.

## Quick introduction ##

exdir is not a file format in itself, but rather a standardized folder structure.
The structure is equivalent to the internal structure of HDF5,
to simplify a transition from either format.
However, data is not stored in a single file, but rather multiple files within
the hierarchy.
The metadata is stored in the YAML format and the binary data in the NumPy
format.

Here is an example structure:

```
example.exdir (File, folder)
│   attributes.yml (-, file)
│   meta.yml (-, file)
│
├── dataset1 (Dataset, folder)
│   ├── data.npy (-, file)
│   ├── attributes.yml (-, file)
│   └── meta.yml (-, file)
│
├── dataset2 (Dataset, folder)
│   ├── data.npz (-, file)
│   └── meta.yml (-, file)
│
└── group1 (Group, folder)
│   ├── attributes.yml (-, file)
    └── meta.yml (-, file)
    │
    ├── dataset3 (Dataset, folder)
    │   ├── data.npy (-, file)
    │   ├── attributes.yml (-, file)
    │   └── meta.yml (-, file)
    │
    ├── link1 (Link, folder)
    │   └── meta.yml (-, file)
    │
    └── dataset4 (Dataset, folder)
        ├── data.npy (-, file)
        ├── attributes.yml (-, file)
        ├── meta.yml (-, file)
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
The metadata of the `File` is stored in a file named meta.yml.
This is internal to exdir.
Attributes of the `File` is stored in a file named attributes.yml.
This is optional.

Below the file, multiple objects may appear, among them `Dataset`s and `Group`s.
Both `Dataset`s and `Group`s are stored as folders in the file system.
Both have their metadata stored in files named meta.yml.
These are not visible as files within the exdir format, but appear simply as
the metadata for the `Dataset`s and `Group`s.

The data within a dataset is stored in a file named data.npy (1D or 2D) or
data.npz (3D).
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

- exdir should be based on existing open standards where suitable to avoid
  solving problems that have already been solved, such as storing binary
  data. 

## Background ##

The exdir was designed due to a need at the Centre for Integrative
Neuroplasticity (CINPLA) at the University of Oslo for a format that would
fit the experimental pipeline.
While researching the different options, we found that the neuroscience
community had several formats for storing experimental data.
A large effort at standardizing the format in the community was spawned by
Neuroscience Without Borders (NWB).
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

## Alternative formats ##

HDF5 is often compared in the above text.
There are also other formats that we have investigated.
Currently, we have only listed ASDF, but other formats will be discussed.

### ASDF ###

- Binary data is stored within YAML text files. 
  This is non-standard and requires additional tools to parse the files.

[1] http://cyrille.rossant.net/moving-away-hdf5/
