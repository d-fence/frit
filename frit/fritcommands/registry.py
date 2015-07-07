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



def factory(Evidences, args, options):
    if 'find' in args:
        logger.info('Starting registry command.')
        args.remove('find')
        find(Evidences, args, options)

