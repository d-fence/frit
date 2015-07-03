#!/usr/bin/python
"""
carving
This command is used to make carving with various tools / methods
An option specifying the tool to use is mandatory (I know, mandatory option is not an option)
Tools :
--photorec
You can choose to carve the whole filesystems or the unallocated space only:
--unalloc
"""
import os
import fritutils
import fritutils.fritlog

logger = fritutils.fritlog.loggers['carvingLog']

def factory(Evidences, args, options):
    if not options:
        fritutils.termout.printWarning("You have to choose the tool to use:")
        fritutils.termout.printWarning("    --photorec")

