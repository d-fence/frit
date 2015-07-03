#!/usr/bin/python
"""
getunalloc
This command is used to extract unallocted space from filesystem when possible.
"""
import os
import fritutils
import fritutils.fritlog

logger = fritutils.fritlog.loggers['getunallocLog']

def getUnalloc(Evidences):
    for evi in Evidences:
        for fs in evi.fileSystems:
            if os.path.exists(fs.unallocDestinationFile):
                logger.warning('Unallocated space file "%s" already exists, not extracting.' % fs.unallocDestinationFile)
                fritutils.termout.printWarning('Unallocated space file "%s" already exists, not extracting.' % fs.unallocDestinationFile)
            else:
                logger.info('Starting to extract unallocted space for "%s/%s".' % (evi.configName,fs.configName))
                fs.blkls()
        if evi.isLocked('getunalloc'):
            evi.umount('getunalloc')

def getSlack(Evidences):
    for evi in Evidences:
        for fs in evi.fileSystems:
            if os.path.exists(fs.slackDestinationFile):
                logger.warning('Slack space file "%s" already exists, not extracting.' % fs.slackDestinationFile)
                fritutils.termout.printWarning('Slack space file "%s" already exists, not extracting.' % fs.slackDestinationFile)
            else:
                logger.info('Starting to extract slack space for "%s/%s".' % (evi.configName,fs.configName))
                fs.blkls(slack=True)
        if evi.isLocked('getunalloc'):
            evi.umount('getunalloc')

def factory(Evidences, args, options):
    if not options:
        # By default, we extract unallocted blocks.
        logger.info('Start getunalloc command.')
        getUnalloc(Evidences)
    else:
        # With the --slack option, we extract the slack space instead
        if options and '--slack' in options:
            logger.info('Start getunalloc command with slack option.')
            getSlack(Evidences)
        else:
            logger.warning('getunalloc command started with unknow arguements.')
            fritutils.termout.printWarning('No valid argument given for the getunalloc command.')
