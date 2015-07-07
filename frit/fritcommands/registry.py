#!/usr/bin/python
"""
registry
This command is made to work on MS Windows registry files.
the "find" command will list all the registry files found.
"""

import os
import fritutils
import fritutils.fritlog

logger = fritutils.fritlog.loggers['registryLog']

def find(Evidences, args, options):
    logger.info('Starting find subcommand.')
    for evi in Evidences:
        for fs in evi.fileSystems:
            for regfilepath in  fs.getRegistryFiles():
                if regfilepath :
                    fritutils.termout.printNormal(regfilepath)

def factory(Evidences, args, options):
    if args and 'find' in args:
        args.remove('find')
        find(Evidences, args, options)
