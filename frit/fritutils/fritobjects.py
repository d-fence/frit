#!/usr/bin/python
"""
This module contains class definitions for frit objects.
Evidence is the base evidence object.
FileSystem is the base file system object.
It also contains evidencesFromConfig that map the Evidences and filesystems
found in config file the objects defined here.
"""

import sys
import re
import os.path
import os
import glob
import fritutils.termout
import fritutils.fritmount
import fritutils.fritdb as fritModel
from sqlalchemy import func

class FileSystem(object):
    """
    This is the basic class for the file systems.
    It have to be overriden for different file systems:
    NTFS, extx, xfs, ...
    """
    def __init__(self,offset,fsConfigName,evidenceConfigName):
        self.rawImage = ''
        self.offset = offset
        self.configName = fsConfigName
        self.evidenceConfigName = evidenceConfigName
        self.fsMountPoint = os.path.join('.frit','filesystems',self.evidenceConfigName,self.configName)
        self.loopLockFile = self.fsMountPoint + 'looplock'
        self.loopDevice = self.getLoopDevice()

    def getLoopDevice(self):
        if os.path.exists(self.loopLockFile):
            lf = open(self.loopLockFile,'r')
            lnum = lf.readline()
            lf.close()
            return lnum
        else:
            return ''

    def writeLoopLock(self):
        if self.loopDevice != '':
            lf = open(self.loopLockFile,'w')
            lf.write(self.loopDevice)
            lf.close()

    def delLoopLock(self):
        if os.path.exists(self.loopLockFile):
            os.remove(self.loopLockFile)

    def acquireLoop(self):
        self.loopDevice = fritutils.fritmount.attachLoopDevice(self.rawImage,self.offset)
        self.writeLoopLock()
        
    def freeLoop(self):
        fritutils.fritmount.detachLoopDevice(self.loopDevice)
        self.loopDevice = ''
        self.delLoopLock()

    def getLockFile(self,locker):
        """
        A function to construct the lockfile
        """
        lockSuffix = '_' + locker + '.lock'
        return self.fsMountPoint + lockSuffix

    def lockList(self):
        llist = []
        lstart = len(self.fsMountPoint) + 1
        for flock in glob.glob(self.fsMountPoint + "*.lock"):
           llist.append(flock[lstart:-5])
        return llist

    def writeLock(self,locker,reason):
        pidReason = "PID: %d -- %s" % (os.getpid(),reason)
        lockFile = self.getLockFile(locker)
        lf = open(lockFile,'a')
        lf.write(pidReason)
        lf.close()

    def removeLock(self,locker):
        lockFile = self.getLockFile(locker)
        try:
            os.remove(lockFile)
        except:
            fritutils.termout.printWarning("Cannot remove lockfile: %s" % lockFile)

    def isLocked(self,locker):
        """
        Check if the filesystem mount is locked by the same action
        """
        llist = self.lockList()
        if locker in llist:
            return True
        else:
            return False

    def isOtherLocked(self,locker):
        """
        Check if the filesystem mount is locked by another action
        """
        lockList = self.lockList()
        if locker in lockList:
            lockList.remove(locker)
        if len(lockList) == 0:
            return False
        else:
            return True

    def makeDirs(self):
        if not os.path.exists(self.fsMountPoint):
            os.makedirs(self.fsMountPoint)

    def isMounted(self):
        """
        Retrun true if this filesystem is mounted
        """
        return os.path.ismount(self.fsMountPoint)

    def listFiles(self):
        if self.isMounted():
            for dirpath, dirs, files in os.walk(self.fsMountPoint):
                for f in files:
                    yield(os.path.join(dirpath,f))
        else:
            firutils.termout.printWarning('%s is not mounted. Cannot list files.' % self.configName)
            sys.exit(1)

    def getEviDb(self):
        """
        A function that return the Evidence model object for this filesystem
        """
        return fritModel.elixir.session.query(fritModel.Evidence).filter_by(configName=fritutils.unicodify(self.evidenceConfigName)).first()

    def getFsDb(self):
        """
        A function that return the Filesystem model object
        """
        eviDb = self.getEviDb()
        cfn = fritutils.unicodify(self.configName)
        return fritModel.elixir.session.query(fritModel.Filesystem).filter_by(configName=cfn, evidence=eviDb).first()

    def dbCountExtension(self,ext):
        """
        A function to get a count and a size sum of the specified extension
        """
        toReturn = {}
        e = fritModel.Extension.query.filter_by(extension=ext).first()
        fso =  self.getFsDb()
        fstate = fritModel.FileState.query.filter_by(state=u'Normal').first()
        fq = fritModel.File.query.filter_by(extension=e,filesystem=fso,state=fstate)
        sizeSum = 0
        sizeSum = fq.value(func.sum(fritModel.File.filesize))
        c = fq.count()
        toReturn['count'] = c
        toReturn['size'] = sizeSum
        return toReturn

    def dbCountFiles(self):
        """
        A function to get a count of files belonging to the filesystem
        """
        toReturn = {}
        for fstate in fritModel.FILESTATES:
            stateDb = fritModel.elixir.session.query(fritModel.FileState).filter_by(state=fstate).first()
            fsDb = self.getFsDb()
            nbFiles = fritModel.elixir.session.query(fritModel.File).filter_by(filesystem=fsDb,state=stateDb).count()
            toReturn[fstate] = nbFiles
        return toReturn

    def ExtensionsFritFiles(self,ext):
        """
        A function that yield a list of files with the specified extension.
        The yielded path is the frit file path.
        """
        e = fritModel.Extension.query.filter_by(extension=ext).first()
        fso =  self.getFsDb()
        fstate = fritModel.FileState.query.filter_by(state=u'Normal').first()
        for fob in fritModel.File.query.filter_by(extension=e,filesystem=fso,state=fstate).all():
            toYield = os.path.join(self.fsMountPoint,fob.fullpath.fullpath[1:],fob.filename)
            yield toYield

    def ExtensionsOriginalFiles(self,ext):
        """
        A function that yield a list of files with the specified extension.
        The yielded path is the original file path on the target system.
        """
        e = fritModel.Extension.query.filter_by(extension=ext).first()
        fso =  self.getFsDb()
        fstate = fritModel.FileState.query.filter_by(state=u'Normal').first()
        for fob in fritModel.File.query.filter_by(extension=e,filesystem=fso,state=fstate).all():
            toYield = os.path.join(fob.fullpath.fullpath[1:],fob.filename)
            yield toYield

class NtfsFileSystem(FileSystem):
    """
    Class for the NTFS file system.
    """
    def getFormat(self):
        return "NTFS"

    def mount(self,locker,reason):
        """
        locker is the intermediate extension given to the lockfile.
        reason is the comment that will be inserted in the lock file.
        """
        # We create needed dirs
        self.makeDirs()
        # if there is no loop device attached, we atatch one
        self.acquireLoop()
        # if the file is not already mounted, we mount it
        if not self.isMounted() and self.loopDevice != '':
            try:
                fritutils.fritmount.ntfs3gMount(self.loopDevice,self.fsMountPoint)
            except fritutils.fritmount.fritMountError:
                self.freeLoop()
                raise
        # we create the lock to prevent other instances to unmount
        self.writeLock(locker,reason)

    def umount(self,locker):
        """
        A function to unmount the filesystem
        """
        #  first we check if the mount is locked by another instance
        if not self.isOtherLocked(locker):
            fritutils.fritmount.fuserUnmount(self.fsMountPoint)
            if self.loopDevice != '':
                self.freeLoop()
        # we remove our lock file
        self.removeLock(locker)

class FatFileSystem(FileSystem):
    """
    Class for the FAT file system.
    """
    def getFormat(self):
        return "FAT"

    def mount(self,locker,reason):
        """
        locker is the intermediate extension given to the lockfile.
        reason is the comment that will be inserted in the lock file.
        """
        # We create needed dirs
        self.makeDirs()
        # if there is no loop device attached, we atach one
        self.acquireLoop()
        # if the file is not already mounted, we mount it
        if not self.isMounted() and self.loopDevice != '':
            try:
                fritutils.fritmount.fatMount(self.loopDevice,self.fsMountPoint)
            except fritutils.fritmount.fritMountError:
                self.freeLoop()
                raise
        # we create the lock to prevent other instances to unmount
        self.writeLock(locker,reason)

    def umount(self,locker):
        """
        A function to unmount the filesystem
        """
        #  first we check if the mount is locked by another instance
        if not self.isOtherLocked(locker):
            fritutils.fritmount.fatUnmount(self.fsMountPoint)
            if self.loopDevice != '':
                self.freeLoop()
        # we remove our lock file
        self.removeLock(locker)

class Evidence(object):
    """
    This is the basic class for evidence files.
    It have to be overriden for different format of evidence files:
    dd,aff,e0 ...
    """
    def __init__(self, filename=None,configName=None):
        self.fileName = filename
        self.configName = configName
        self.fileSystems = []
        self.rawImage = ''
        self.containerMountPoint = os.path.join('.frit','containers',self.configName)

    def mount(self,*args):
        """
        A function to mount the evidence.
        If not needed, just leave it empty.
        """
        pass

    def umount(self,*args):
        """
        A function to umount the evidence.
        If not needed, just leave it empty.
        """
        pass

    def getLockFile(self,locker):
        """
        A function to construct the lockfile
        """
        lockSuffix = '_' + locker + '.lock'
        return self.containerMountPoint + lockSuffix
        
    def lockList(self):
        llist = []
        lstart = len(self.containerMountPoint) + 1
        for flock in glob.glob(self.containerMountPoint + "*.lock"):
           llist.append(flock[lstart:-5])
        return llist
        
    def writeLock(self,locker,reason):
        lockFile = self.getLockFile(locker)
        lf = open(lockFile,'a')
        lf.write(reason)
        lf.close()

    def removeLock(self,locker):
        lockFile = self.getLockFile(locker)
        try:
            os.remove(lockFile)
        except:
            fritutils.termout.printWarning("Cannot remove lockfile: %s" % lockFile)

    def isLocked(self,locker):
        llist = self.lockList()
        if locker in llist:
            return True
        else:
            return False

    def isMounted(self):
        """
        Retrun true if this  is mounted
        have to be overriden by the different filesystems
        """
        pass

class DdEvidence(Evidence):
    def populateRawImage(self):
        """
        This function populate the raw image filename to all filesystems of the Evidence.
        Even if this file does not exists yet.
        """
        self.rawImage = self.fileName
        for fs in self.fileSystems:
            fs.rawImage = self.rawImage   

class AffEvidence(Evidence):
    def isMounted(self):
        return os.path.ismount(self.containerMountPoint)
            
    def populateRawImage(self):
        """
        This function populate the raw image filename to all filesystems of the Evidence.
        Even if this file does not exists yet.
        """
        self.rawImage = os.path.join(self.containerMountPoint, os.path.basename(self.fileName) + '.raw')
        for fs in self.fileSystems:
            fs.rawImage = self.rawImage    

    def mount(self,locker,reason):
        """
        locker is the intermediate extension given to the lockfile.
        reason is the comment that will be inserted in the lock file.
        """
        # We create needed dirs
        if not os.path.exists(self.containerMountPoint):
            os.makedirs(self.containerMountPoint)
        # if the file is not already mounted, we mount it
        if not os.path.ismount(self.containerMountPoint):
                fritutils.fritmount.affMount(self.fileName,self.containerMountPoint)
        # we create the lock to prevent other instances to unmount
        self.writeLock(locker,reason)
        
    def umount(self,locker):
        """
        A function to unmount the container
        """
        lockList = self.lockList()
        if locker in lockList:
            lockList.remove(locker)
        if len(lockList) == 0:
            # as it is a container, we have to try to unmount filesystems first
            safeToUnmount = True
            for fs in self.fileSystems:
                if fs.isLocked(locker):
                    fritutils.termout.printMessage('\tUnmounting filesystems "%s" first' % fs.configName)
                    fs.umount(locker)
                    # if at least one fs is still in use, we cannot unmount
                    if len(fs.lockList()) != 0:
                        print fs.lockList()
                        safeToUnmount = False
                elif fs.isOtherLocked(locker):
                    # Not safe to unmount container because locked by another thing
                    safeToUnmount = False
            if safeToUnmount:   
                fritutils.fritmount.fuserUnmount(self.containerMountPoint)
            else:
                fritutils.termout.printWarning('\tSome filsystems are still in use, not unmounting %s' % self.fileName)
        else:
            fritutils.termout.printWarning('Evidence "%s" is still locked by other instances of frit. Not unmounting' % self.fileName)
        # we remove our lock file
        self.removeLock(locker)

class EwfEvidence(Evidence):
    pass
    
def evidencesFromConfig(fritConf,verbose):
    """
    A function that parse a configObj and map the Evidences to Evidence object.
    """
    if verbose:
        fritutils.termout.printMessage("Parsing config file.")
    Evidences = []
    EviRegex = re.compile("^Evidence\d+")
    FsRegex = re.compile("^Filesystem\d+")
    ValidFileSystems = ('FAT','NTFS')
    ev = ''
    for key in fritConf.keys():
        if EviRegex.search(key):
            format = fritConf[key]['Format']
            if format == 'aff':
                ev = AffEvidence(filename=fritConf[key]['Name'],configName=key)
            elif format == 'dd':
                ev = DdEvidence(filename=fritConf[key]['Name'],configName=key)
            elif format == 'ewf':
                ev = EwfEvidence(filename=fritConf[key]['Name'],configName=key)
            else:
                fritutils.termout.printWarning('No valid format found.')
                sys.exit(1)
            if verbose:
                fritutils.termout.printSuccess("\t" + ev.fileName + " Found.")
            fs = ''
            for subkey in fritConf[key].keys():
                if FsRegex.search(subkey):
                    if fritConf[key][subkey]['Format'] == 'NTFS':
                        off = fritutils.getOffset(fritConf[key][subkey]['Offset'])
                        fs = NtfsFileSystem(offset=off,fsConfigName=subkey,evidenceConfigName=ev.configName)
                        ev.fileSystems.append(fs)
                        ev.populateRawImage()
                        if verbose:
                            fritutils.termout.printSuccess("\t\t NTFS filesystem Found at offset %d." % fs.offset)
                    elif fritConf[key][subkey]['Format'] == 'FAT':
                        off = fritutils.getOffset(fritConf[key][subkey]['Offset'])
                        fs = FatFileSystem(offset=off,fsConfigName=subkey,evidenceConfigName=ev.configName)
                        ev.fileSystems.append(fs)
                        ev.populateRawImage()
                        if verbose:
                            fritutils.termout.printSuccess("\t\t FAT filesystem Found at offset %d." % fs.offset)
                    elif fritConf[key][subkey]['Format'] not in ValidFileSystems:
                        fritutils.termout.printWarning("%s This filesystem type (%s) is unknow by frit." % (ev.configName,fritConf[key][subkey]['Format']))

            Evidences.append(ev)

    if len(Evidences) ==0:
        fritutils.termout.printWarning("No evidences found in config file.")
        sys.exit(1)
    return Evidences
