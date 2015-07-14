#!/usr/bin/python
"""
vshadow
This command is made to work with MS Volume shadow copies.
The "list" subcommand will list all shadow copies found on NTFS FS
"""

import os
import fritutils
import fritutils.fritlog
import pyvshadow

logger = fritutils.fritlog.loggers['vshadowLog']

def vshadowList(Evidences, ags, options):
    for evi in Evidences:
        for fs in evi.fileSystems:
            print "FS"


def factory(Evidences, args, options):
    if args and 'list' in args:
        vshadowList(Evidences, args, options)
