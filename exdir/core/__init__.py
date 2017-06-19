"""
.. module:: exdir.core
.. moduleauthor:: Svenn-Arne Dragly, Milad H. Mobarhan, Mikkel E. Lepperød
"""

from __future__ import print_function, division, unicode_literals

import os
import numpy as np
import shutil
import quantities as pq
import re

from .exdir_object import Object
from .exdir_file import File
from .attribute import Attribute
from .dataset import Dataset
from .group import Group
from .raw import Raw
