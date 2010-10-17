#!/usr/bin/python
"""
Utilities extract emails from different type of mailboxes
"""

import subprocess
import os
import os.path
import re
import fritutils.termout

PFFEXPORT = '/usr/bin/pffexport'

def pffExport(pstFile,destination):
    fritutils.termout.printMessage('\tExporting "%s" to "%s".' % (pstFile,destination))
    pffexport = subprocess.Popen([PFFEXPORT, '-f', 'text', '-m', 'all', '-t', destination, pstFile])
    pffexport.wait()
    if  pffexport.returncode > 0:
        print "Error with pffexport"
    print "Successfuly exported pst file."

