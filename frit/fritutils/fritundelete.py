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
TSKRECOVER = '/usr/bin/tsk_recover'

def NtfsUndelete(lodevice,destination):
    fritutils.termout.printMessage('\tNTFS Undeleting "%s" to "%s".' % (lodevice,destination))
    ntfsundelete = subprocess.Popen([NTFSUNDELETE, '-p', '100', '-u', '-m', '*', '-d', destination, '-f', lodevice])
    ntfsundelete.wait()
    if ntfsundelete.returncode > 0:
        print "Error with ntfsundelete"
    print "Successful undelete."
    
def TskUndelete(lodevice,destination):
    fritutils.termout.printMessage('\ttsk_recover Undeleting "%s" to "%s".' % (lodevice,destination))
    tskundelete = subprocess.Popen([TSKRECOVER, lodevice, destination])
    tskundelete.wait()
    if tskundelete.returncode > 0:
        print "Error with tskundelete"
    print "Successful undelete."
