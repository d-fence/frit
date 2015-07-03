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

def photorec(Evidences, args, options):
    logger.info('Starting carving with photorec.')

def factory(Evidences, args, options):
    # At least, the tool to use is mandatory
    if not options:
        fritutils.termout.printWarning("You have to choose the tool to use:")
        fritutils.termout.printWarning("    --photorec")
        return

    # We have to extract unallocated files first if we want to carve them
    if '--unalloc' in options:
        pass

    if '--photorec' in options:
        options.remove('--photorec')
        photorec(Evidences, args, options)

