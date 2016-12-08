# -*- coding: utf-8 -*-
"""
This is the implementation of the NEO IO for the eds format.
Depends on: scipy
            h5py >= 2.5.0
            numpy
            quantities
Supported: Read
Authors: Milad H. Mobarhan @CINPLA,
         Svenn-Arne Dragly @CINPLA,
         Mikkel E. Lepperød @CINPLA
"""

from __future__ import division
from __future__ import print_function
from __future__ import with_statement

import sys
from neo.io.baseio import BaseIO
from neo.core import (Segment, SpikeTrain, Unit, Epoch, AnalogSignal,
                      ChannelIndex, Block, IrregularlySampledSignal)
import neo.io.tools
import numpy as np
import quantities as pq
import os
import glob

python_version = sys.version_info.major
if python_version == 2:
    from future.builtins import str


import eds

class EdsIO(BaseIO):
    """
    Class for reading/writting of eds fromat
    """
    
    is_readable = False
    is_writable = True

    supported_objects = [Block, Segment, AnalogSignal, ChannelIndex, SpikeTrain]
    readable_objects = []
    writeable_objects = []

    has_header = False
    is_streameable = False

    name = 'eds'
    description = 'This IO reads experimental data from an eds folder'
    
    # mode can be 'file' or 'dir' or 'fake' or 'database'
    # the main case is 'file' but some reader are base on a directory or a database
    # this info is for GUI stuff also
    mode = 'dir'

    def __init__(self, folder):
        """
        Arguments:
            folder : the folder
        """
        BaseIO.__init__(self)
        self._absolute_folder = folder
        self._path, relative_folder = os.path.split(folder)
        self._base_folder, extension = os.path.splitext(relative_folder)
        
        print ("base=", self._base_folder, extension)
        
        if extension != ".eds":
            raise ValueError("folder extension must be '.eds'")
            
        self._eds_folder = eds.File(folder=folder, mode="a")
            
    
    def write_spiketrain(self):
        pass
        
    
            
    def read_analogsignal(self):
        # TODO implement read analog signal
        pass
        
    def read_spiketrain(self):
        # TODO implement read spike train
        pass
        
    def read_epoch(self):
        # TODO read epoch data
        pass    
        
    def read_block(self):
        # TODO read block
        pass
            
        
        
        
        

if __name__ == "__main__":
    import sys
    testfile = "/tmp/test.eds"
    io = EdsIO(testfile)
    

    
    
    
