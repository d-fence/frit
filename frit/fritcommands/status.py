#!/usr/bin/python
"""
status command
"""

import os.path
import fritutils.termout

def status(Evidences,args):
    """
    Print a status report for all evidences
    """
    clean = False
    if args:
        if 'clean' in args:
            clean = True
    fritutils.termout.printMessage("Frit Status:")
    for evi in Evidences:
        fritutils.termout.printMessage('\t%s : %s' % (evi.configName,evi.fileName))
        if evi.isMounted():
            fritutils.termout.printNormal('\tMounted on : %s' % evi.containerMountPoint)
        locklist = evi.lockList()
        if len(locklist) > 0:
            ll = ' '.join(locklist)
            fritutils.termout.printNormal('\t\tLocked by: %s' % ll)
            # if the Evidence is not mounted and at least a lockfile, we have an inconsistency
            if not evi.isMounted():
                fritutils.termout.printWarning('\t\tInconsistency: %s is locked but not mounted. Use the "status clean" command to remove this lock file.' % evi.configName)
                if clean:
                    for lock in locklist:
                        fritutils.termout.printNormal('\t\tremoving lock: %s' % lock)
                        evi.removeLock(lock)
        else:
            # if the Evidence is mounted with no lockfile we have an incosistency
            if evi.isMounted():
                fritutils.termout.printWarning('\t\tInconsistency: %s is mounted with no lockfile. Use the "status clean" command to unmount.' % evi.configName)
                if clean:
                    fritutils.termout.printWarning('\t\tUnmounting')
                    evi.writeLock("clean","Cleaining inconsistencies")
                    evi.umount("clean")
        if len(evi.fileSystems) > 0:
            for fs in evi.fileSystems:
                fritutils.termout.printMessage('\t\t%s (format: %s , offset: %d)' % (fs.configName, fs.getFormat(),fs.offset))
                ld = fs.getLoopDevice()
                if ld != '':
                    fritutils.termout.printNormal('\t\tAssociated with loop device: %s' % ld)
                if fs.isMounted():
                    fritutils.termout.printNormal('\t\tMounted on : %s' % fs.fsMountPoint)
                fsLockList = fs.lockList()
                if len(fsLockList) > 0:
                    fsll = ' '.join(fsLockList)
                    fritutils.termout.printNormal('\t\t\tLocked by: %s' % fsll)
                    if not fs.isMounted():
                        #if the filesystem is not mounted and at least a lockfile, we have an inconsistency
                        fritutils.termout.printWarning('\t\t\tInconsistency: %s is locked but not mounted. Use the "status clean" command to remove this lock file.' % fs.configName)
                        if clean:
                            for lock in fsLockList:
                                fritutils.termout.printNormal('\t\t\tremoving lock: %s' % lock)
                                fs.removeLock(lock)
                else:
                    # if the filesystem as no lockfile and is mounted, we have a problem
                    if fs.isMounted():
                        fritutils.termout.printWarning('\t\t\tInconsistency: %s is mounted without lockfile. Use the "status clean" command to unmount.' % fs.configName)
                        if clean:
                            fritutils.termout.printNormal("\t\t\tUmounting")
                            fs.writeLock("clean","Cleaning inconsistencies")
                            fs.umount("clean")


    # Now we check the database status
    fritutils.termout.printMessage("Frit Database Status:")
    if os.path.exists('.frit/frit.sqlite'):
        for evi in Evidences:
            fritutils.termout.printMessage('\t%s (%s):'% (evi.configName, evi.fileName))
            for fs in evi.fileSystems:
                fritutils.termout.printMessage('\t\t%s:' % fs.configName)
                counts = fs.dbCountFiles()
                for t,c in counts.iteritems():
                    fritutils.termout.printMessage('\t\t\t%s files: %d' % (t,c))
    else:
        fritutils.termout.printMessage('No Database found, use the "store create" command to create one')
