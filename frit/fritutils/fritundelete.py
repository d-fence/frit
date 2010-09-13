#!/usr/bin/python
"""
Utilities to perform an undelete on various filesystems
"""

import subprocess
import os
import os.path
import re
import fritutils.termout

NTFSUNDELETE = '/usr/sbin/ntfsundelete'

def NtfsUndelete(lodevice,destination):
    fritutils.termout.printMessage('\tNTFS Undeleting "%s" to "%s".' % (lodevice,destination))
    ntfsundelete = subprocess.Popen([NTFSUNDELETE, '-p', '100', '-u', '-m', '*', '-d', destination, '-f', lodevice])
    ntfsundelete.wait()
    if ntfsundelete.returncode > 0:
        print "Error with ntfsundelete"
    print "Successful undelete."
