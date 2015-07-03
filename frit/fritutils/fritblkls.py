#!/usr/bin/python
"""
Utilities to extract unallocted blocks from various filesystems
"""

import subprocess
import os
import os.path
import re
import fritutils.termout
from fritutils.fritglobals import *

def Blkls(lodevice,destination,slack):
    """
    lodevice: the loopback device on which to perform blkls
    destination: the destination dir
    slack: A boolean flag to decide to extract slack or not
    """
    with open(destination,'wb') as outFile:
        fritutils.termout.printMessage('\tExtracting unallocated blocks from "%s" to "%s".' % (lodevice,destination))
        if slack:
            blkls = subprocess.Popen([BLKLS, '-s', lodevice ], stdout=outFile)
        else:
            blkls = subprocess.Popen([BLKLS, lodevice ], stdout=outFile)
        blks.wait()
        if blkls.returncode > 0:
            fritutils.termout.printWarning("Error with blkls")
        fritutils.termout.printSuccess("Successfully extracted unallocated blocks")
