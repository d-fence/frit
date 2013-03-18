#!/usr/bin/python
"""
mmls support. A good way to find unused sectors.
"""

import subprocess
import os
import os.path
import fritutils.termout
from fritutils.fritglobals import *

def getUnallocatedSectors(container):
    """
    This function is used by Evidences objects to get a list of dict containing
    the unallocated sectors.
    """
    secList = []
    if os.path.exists(container):
        mmls = subprocess.Popen([MMLS, container], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mmls.wait()
        for line in mmls.stdout.readlines():
            d = {}
            if 'Unallocated' in line:
                s = line.split()
                if len(s) > 0:
                    start = int(s[2])
                    end = int(s[3])
                    d['start'] = start
                    d['end'] = end
                    secList.append(d)
    return secList
       


