#!/usr/bin/python
"""
Mount command
"""

import fritutils

logger = fritutils.fritlog.loggers['mountLog']

def Mount(Evidences,fullMount=False):
    """
    Mount all evidences containers and then all filesystems
    Only to be used by the "mount" command isued by the user.
    """
    fritutils.termout.printMessage("Mounting all evidences and file systems")
    for evi in Evidences:
        # first, we check if the evidence is not already "user" locked
        if evi.isLocked("user"):
            fritutils.termout.printWarning('\tEvidence "%s" is already mounted by the user. Not mounting.' % evi.fileName)
        else:
            # First we check if the file still exists
            if evi.exists():
                fritutils.termout.printMessage("\tMounting " + evi.fileName + ". Please wait.")
                evi.mount("user","Mounted by the user\n")
                logger.info('Evidence %s succesfully mounted' % evi.configName)
                fritutils.termout.printSuccess("\t" + evi.fileName + " mounted")
                if fullMount:
                    for fs in evi.fileSystems:
                        try:
                            logger.info('Trying to mount filesystem %s' % evi.configName + '/' + fs.configName)
                            fs.mount("user","Mounted by the user\n")
                        except fritutils.fritmount.fritMountError:
                            logger.warning('Unable to mount filesystem %s' % evi.configName + '/' + fs.configName)
                            fritutils.termout.printWarning('\tUnable to mount filsystem %s' % fs.configName)
            else:
                fritutils.termout.printWarning('File "%s", not found ! not mounting.' % evi.fileName)
                logger.warning('Evidence container file "%s" was not found on the system, unable to mount.' % evi.fileName)

def Umount(args):
    """
    Unmount all evidences filesystems and then containers
    Only to be used by the "umount" command isued by the user.
    """
    logger.info('umount command started.')
    fritConfig = fritutils.getConfig()
    Evidences = fritutils.getEvidencesFromArgs(args,fritConfig,logger=logger)
    fritutils.termout.printMessage("Unmounting evidences.")
    for evi in Evidences:
        if evi.isLocked("user"):
            fritutils.termout.printMessage("\tUnmounting " + evi.fileName + ". please wait.")
            evi.umount("user")
        else:
            fritutils.termout.printMessage('\tEvidence "%s" is not locked by the user. Not unmounting.' % evi.fileName)
            # we have to verify if filesystems are locked by the user and umount them as requested
            for fs in evi.fileSystems:
                if fs.isLocked("user"):
                    fritutils.termout.printMessage("\tUnmounting " + fs.configName + ". please wait.")
                    fs.umount("user")

def mountCommand(args):
    """
    Handles the mount command and if 'containers' is specified in args, it only mount containers.
    """
    logger.info('mount command started.')
    fritConfig = fritutils.getConfig()
    Evidences = fritutils.getEvidencesFromArgs(args,fritConfig,logger=logger)
    if args.containers:
        logger.info('Only mounting containers as requested by the user.')
        Mount(Evidences)
    else:
        logger.info('Mounting containers and filesystems.')
        Mount(Evidences,fullMount=True)
