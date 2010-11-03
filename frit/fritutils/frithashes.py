#!/usr/bin/python
"""
Compute hashes for the given file.
"""

import subprocess
import os
import os.path
import hashlib
import fritutils.termout

SSDEEP='/usr/bin/ssdeep'

def getSsdeep(fullpath):
    ssdeep = subprocess.Popen([SSDEEP, fullpath], stdout=subprocess.PIPE)
    ssdeep.wait()
    output = ssdeep.stdout.readlines()[1]
    print output

def getSize(fullpath):
    try:
        stats = os.stat(fullpath)
    except:
        fritutils.termout.printWarning("Problem getting stats on %s" % fullpath)
        return 0
    return stats.st_size

def hashes(fullpath):
    """
    Return a tuple of hexdigests for:
    md5, sha1, sha256, ssdeep
    """
    size = getSize(fullpath)
    if size == 0:
        return ("Zero file size", "Zero file size", "Zero file size", "Zero file size")
    
    try:
        fic = open(fullpath,"rb")
        data = fic.read()
    except (IOError,MemoryError):
        return ("Problematic file", "Problematic file", "Problematic file", "Problematic file")
    else:
        md5 = hashlib.md5(data).hexdigest()
        sha1 = hashlib.sha1(data).hexdigest()
        sha256 = hashlib.sha256(data).hexdigest()
        getSsdeep(fullpath)
        print md5
        print sha1
        print sha256
        
