#!/usr/bin/python
"""
hashes command.
Computes files hashes (md5, sha1 ans ssdeep).
"""

import os
import sys
import fritutils.termout
import fritutils.fritobjects
import fritutils.fritdb as fritModel
import fritutils.frithashes

def factory(Evidences,args):
    # First we check if the database exists
    if not os.path.exists(fritModel.DBFILE):
        fritutils.termout.printWarning('Datase does not exists yet. You should create it first with the store command.')
        sys.exit(1)
    for evi in Evidences:
        for fs in evi.fileSystems:
            fs.mount('hashes', 'Hashing files')
            for f in fs.listFiles():
                fritutils.frithashes.hashes(f)
            fs.umount('hashes')
