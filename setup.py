# -*- coding: utf-8 -*-
from setuptools import setup
import os

from setuptools import setup, find_packages

long_description = open("README.md").read()

entry_points = None


install_requires = []

setup(name="exdir",
      packages=find_packages(),
      entry_points=entry_points,
      include_package_data=True,
      )
