#!/usr/bin/python
"""
status command
"""

import os.path
import fritutils.termout

def dbStatus(Evidences):
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

def status(Evidences,args):
    """
    Print a status report for all evidences
    """
    clean = False
    if args:
        if 'database' in args:
            dbStatus(Evidences)
            return
        elif 'clean' in args:
            clean = True
    fritutils.termout.printMessage("Frit Status:")
    for evi in Evidences:
        fritutils.termout.printMessage('\t%s : %s' % (evi.configName,evi.fileName))
        if evi.isMounted() and evi.getFormat() != 'dd':
            fritutils.termout.printNormal('\tMounted on : %s' % evi.containerMountPoint)
        locklist = evi.lockList()
        if len(locklist) > 0:
            fritutils.termout.printNormal('\t\tLocked by: %s' % evi.lockListString())
            # if the Evidence is not mounted and at least a lockfile, we have an inconsistency
            if not evi.isMounted():
                fritutils.termout.printWarning('\t\tInconsistency: %s is locked but not mounted. Use the "status clean" command to remove this lock file.' % evi.configName)
                if clean:
                    for lock in locklist:
                        fritutils.termout.printNormal('\t\tremoving lock: %s' % lock)
                        evi.removeLock(lock)
            else:
                # If the Evidence is mounted and there is no running process we probably have a problem
                for lock in locklist:
                    # "user" lock is a special case because there is no running process involved.
                    if lock != "user":
                        if not evi.isRunning(lock):
                            fritutils.termout.printWarning('\t\tInconsistency: %s is locked and mounted but the locker is not running. Use the "status clean" command to remove this lock file.' % evi.configName)
                        if clean:
                            # we simply remove the lock file. It will create another inconsitsency, up to the user to clean it.
                            fritutils.termout.printNormal('\t\tremoving lock: %s' % lock)
                            evi.removeLock(lock)
        else:
            # if the Evidence is mounted with no lockfile we have an inconsistency
            if evi.isMounted() and evi.getFormat() != 'dd' :
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
                    fritutils.termout.printNormal('\t\tLoop device "%s" is locked by %s' % (ld,fs.configName))
                    if not fs.verifyLoopDevice():
                        if clean:
                            fritutils.termout.printNormal('\t\tremoving lock: %s' % fs.loopLockFile)
                            fs.delLoopLock()
                        else:
                            fritutils.termout.printWarning('\t\tInconsistency: "%s" is not really associated with "%s". Use the "status clean" command to remove the lock.' % (fs.rawImage,fs.loopDevice))
                if fs.isMounted():
                    fritutils.termout.printNormal('\t\tMounted on : %s' % fs.fsMountPoint)
                fsLockList = fs.lockList()
                if len(fsLockList) > 0:
                    fritutils.termout.printNormal('\t\t\tLocked by: %s' % fs.lockListString())
                    if not fs.isMounted():
                        #if the filesystem is not mounted and at least a lockfile, we have an inconsistency
                        fritutils.termout.printWarning('\t\t\tInconsistency: %s is locked but not mounted. Use the "status clean" command to remove this lock file.' % fs.configName)
                        if clean:
                            for lock in fsLockList:
                                fritutils.termout.printNormal('\t\t\tremoving lock: %s' % lock)
                                fs.removeLock(lock)
                    else:
                        # if the filesystem is mounted with a lockfile and no running process, we have a problem
                        for lock in fsLockList:
                            # "user" lock is a special case because there is no running process involved
                            if lock != "user":
                                if not fs.isRunning(lock):
                                    fritutils.termout.printWarning('\t\t\tInconsistency: %s is locked and mounted but the process is not running anymore. Use the "status clean" command to remove this lock file.' % fs.configName)
                                if clean:
                                    # we simply remove the lock, this will create another inconsistency, up to the user to clean it.
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



