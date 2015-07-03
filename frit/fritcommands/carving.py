#!/usr/bin/python
"""
carving
This command is used to make carving with various tools / methods
An option specifying the tool to use is mandatory (I know, mandatory option is not an option)
Tools :
--photorec
You can choose to carve the whole filesystems or the unallocated space only:
--unalloc
If you want to carve the whole container, you have to use this option:
--whole
"""
import os
import fritutils
import fritutils.fritlog
import fritutils.fritcarving
import getunalloc

logger = fritutils.fritlog.loggers['carvingLog']

def photorec(Evidences, args, options):
    logger.info('Starting carving with photorec.')
    if '--unalloc' in options:
        logger.info('Working on unallocted files')
        for evi in Evidences:
            for fs in evi.fileSystems:
                target = fs.unallocDestinationFile
                if os.path.exists(target):
                    # Creation of the destination dir
                    destdir = os.path.join('.frit/extractions/carving/photorec/unallocated',evi.configName, fs.configName)
                    if not os.path.exists(destdir):
                        os.makedirs(desdir)
                    fritutils.fritcarving.Photorec(target,destdir)
    elif '--whole' in options:
        logger.info('Working on whole containers')
    else:
        logger.info('Working on whole filesystems')


def factory(Evidences, args, options):
    # At least, the tool to use is mandatory
    if not options:
        fritutils.termout.printWarning("You have to choose the tool to use:")
        fritutils.termout.printWarning("    --photorec")
        return

    # We have to extract unallocated files first if we want to carve them
    if '--unalloc' in options:
        getunalloc.getUnalloc(Evidences)

    if '--photorec' in options:
        options.remove('--photorec')
        photorec(Evidences, args, options)

