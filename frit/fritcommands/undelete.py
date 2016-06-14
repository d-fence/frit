#!/usr/bin/python
"""
undelete
This command is used to undelete files from filesystems when possible.
"""
import os
import fritutils
import fritutils.fritlog

logger = fritutils.fritlog.loggers['undeleteLog']

def dirFull(destination):
    if os.path.exists(destination):
        if len(os.listdir(destination)) > 0:
            return True
    return False

def undelete(Evidences):
    for evi in Evidences:
        for fs in evi.fileSystems:
            if dirFull(fs.undeleteDestination):
                logger.warning('Directory "%s" is not empty. Not trying to undelete.' % fs.undeleteDestination)
                fritutils.termout.printWarning('Directory "%s" is not empty. Not trying to undelete.' % fs.undeleteDestination)
            else:
                logger.info('Starting to undelete files for "%s/%s".' % (evi.configName,fs.configName))
                fs.undelete()
        # As the undelete method locked and maybe mounted the container,
        # we have to remove the undelete lock and umount its container
        # Because it's not handeled by the object to avoid race conditions.
        if evi.isLocked('undelete'):
            evi.umount('undelete')

def listUndeleted(Evidences):
    for evi in Evidences:
        for fs in evi.fileSystems:
            for f in fs.listUndeleted():
                fritutils.termout.printNormal(f)

def factory(args):
    fritConfig = fritutils.getConfig()
    Evidences = fritutils.getEvidencesFromArgs(args,fritConfig,logger=logger)
    if args.list:
        logger.info('Listing undeleted files.')
        listUndeleted(Evidences)
    else:
        logger.info('Start undelete command.')
        undelete(Evidences)
