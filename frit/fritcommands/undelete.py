#!/usr/bin/python
"""
undelete
This command is used to undelete files from filesystems when possible.
"""
import fritutils

def factory(Evidences, args):
    for evi in Evidences:
        for fs in evi.fileSystems:
            fs.undelete()
