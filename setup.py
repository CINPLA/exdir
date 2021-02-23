# -*- coding: utf-8 -*-
from setuptools import setup
import os

from setuptools import setup, find_packages
import versioneer


long_description = open("README.md", encoding="utf-8").read()

install_requires = []

setup(
    name="exdir",
    packages=find_packages(),
    include_package_data=True,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    data_files=[
        # like `jupyter nbextension install --sys-prefix`
        (
            "share/jupyter/nbextensions/exdir",
            [
                "exdir/static/index.js",
            ],
        ),
        # like `jupyter nbextension enable --sys-prefix`
        (
            "etc/jupyter/nbconfig/notebook.d",
            ["jupyter-config/nbconfig/notebook.d/exdir.json"],
        ),
        # like `jupyter serverextension enable --sys-prefix`
        (
            "etc/jupyter/jupyter_notebook_config.d",
            ["jupyter-config/jupyter_notebook_config.d/exdir.json"],
        ),
    ],
    install_requires=[
        "numpy>=1.20",
        "ruamel.yaml>=0.16",
        "six>=1.15",
    ],
    zip_safe=False,
)
