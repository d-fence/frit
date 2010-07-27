#!/usr/bin/python
"""
Mount command
"""

import fritutils.termout

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
            fritutils.termout.printMessage("\tMounting " + evi.fileName + ". Please wait.")
            evi.mount("user","Mounted by the user\n")
            fritutils.termout.printSuccess("\t" + evi.fileName + " mounted")
            if fullMount:
                for fs in evi.fileSystems:
                    try:
                        fs.mount("user","Mounted by the user\n")
                    except fritutils.fritmount.fritMountError:
                        fritutils.termout.printWarning('\tUnable to mount filsystem %s' % fs.configName) 

def Umount(Evidences):
    """
    Unmount all evidences filesystems and then containers
    Only to be used by the "umount" command isued by the user.
    """
    fritutils.termout.printMessage("Unmounting all evidences.")
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

def mountCommand(Evidences,args):
    """
    Handles the mount command and if 'containers' is specified in args, it only mount containers.
    """
    if args:
        if 'containers' in args:
            Mount(Evidences)
        else:
            fritutils.termout.printWarning('Unknown mount command parameters : "%s"' % args)
    else:
        Mount(Evidences,fullMount=True)
