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
import fritutils.fritundelete
import fritutils.fritdb as fritModel
import fritutils.fritlog
from sqlalchemy import func

logger = fritutils.fritlog.loggers['fritobjectsLog']

class FileSystem(object):
    """
    This is the basic class for the file systems.
    It have to be overriden for different file systems:
    NTFS, extx, xfs, ...
    """
    def __init__(self,offset,fsConfigName,evidence):
        self.rawImage = ''
        self.offset = offset
        self.evidenceConfigName = evidence.configName
        self.evidence = evidence
        self.configName = fsConfigName
        self.fsMountPoint = os.path.join('.frit','filesystems',self.evidenceConfigName,self.configName)
        self.loopLockFile = self.fsMountPoint + 'looplock'
        self.loopDevice = self.getLoopDevice()
        self.undeleteDestination = unicode(os.path.join('.frit/extractions/undeleted/',evidence.configName,self.configName))

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
        if self.loopDevice == '':
            self.loopDevice = fritutils.fritmount.attachLoopDevice(self.rawImage,self.offset)
            logger.info('Aquired a loop device: %s' % self.loopDevice)
            self.writeLoopLock()

    def freeLoop(self):
        logger.info('Detaching loop device %s' % self.loopDevice)
        try:
            fritutils.fritmount.detachLoopDevice(self.loopDevice)
        except fritutils.fritmount.fritMountError:
            fritutils.termout.printWarning('Filesystem %s was not able to detach itself from %s' % (self.rawImage, self.loopDevice))
            logger.warning('Filesystem %s was not able to detach itself from %s' % (self.rawImage, self.loopDevice))
        finally:
            self.loopDevice = ''
            self.delLoopLock()

    def verifyLoopDevice(self):
        return fritutils.fritmount.verifyLoopDevice(self.loopDevice,self.rawImage)

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

    def lockListString(self):
        """
        Return a locklist in form of a string
        With the PID included
        """
        lstring = ''
        for l in self.lockList():
            lstring += l 
            p = ' '.join(self.getPids(l))
            lstring += ' (PIDS: ' + p + ') '
        return lstring

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

    def getPids(self,locker):
        pidlist = []
        lockFile = self.getLockFile(locker)
        lf = open(lockFile,'r')
        for line in lf.readlines():
            pid = line.split(': ')[1].split(' -- ')[0]
            pidlist.append(pid)
        lf.close()
        return pidlist

    def isRunning(self,locker):
        """
        Return True if at least a locker as a running PID
        """
        if not self.isLocked(locker):
            return None
        else:
            for pid in self.getPids(locker):
                procfile = os.path.join('/proc/',pid)
                if os.path.exists(procfile):
                    return True
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

    def makeUndelDir(self):
        if not os.path.exists(self.undeleteDestination):
            os.makedirs(self.undeleteDestination)

    def isMounted(self):
        """
        Retrun true if this filesystem is mounted
        """
        return os.path.ismount(self.fsMountPoint)

    def mountCommand(self):
        """
        A function to be overriden by specific mount commands
        """
        pass
    
    def umountCommand(self):
        """
        A function to be overriden by specific umount commands
        """
        pass

    def mount(self,locker,reason):
        """
        locker is the intermediate extension given to the lockfile.
        reason is the comment that will be inserted in the lock file.
        """
        # We check if the Evidence is mounted
        # if not, we mount it for the same reason
        # if yes, we check if we need to lock it
        if not self.evidence.isMounted():
            logger.info('Mounting evidence "%s" from filesystem object.' % self.evidence.configName)
            self.evidence.mount(locker,reason)
        else:
            if not self.evidence.isLocked(locker):
                logger.info('Evidence "%s" is mounted but mounting to acquire a lock from filesystem object.' % self.evidence.configName)
                self.evidence.mount(locker,reason)
            
        # We create needed dirs
        self.makeDirs()
        # if there is no loop device attached, we atatch one
        self.acquireLoop()
        # if the file is not already mounted, we mount it
        if not self.isMounted() and self.loopDevice != '':
            try:
                self.mountCommand()
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
            self.umountCommand()
            if self.loopDevice != '':
                self.freeLoop()
        # we remove our lock file
        self.removeLock(locker)
        # The caller have to umount the container by itself.
        # We have some race condition if we try to do it here.

    def listFiles(self):
        if self.isMounted():
            for dirpath, dirs, files in os.walk(self.fsMountPoint):
                dirpath = dirpath.decode('utf-8')
                for f in files:
                    if not isinstance(f,unicode):
                        f = f.decode('utf-8')
                    yield(os.path.join(dirpath,f))
        else:
            fritutils.termout.printWarning('%s is not mounted. Cannot list files.' % self.configName)
            sys.exit(1)

    def listUndeleted(self):
        logger.info('Listing undeleted files for "%s".' % self.configName)
        for dirpath, dirs, files in os.walk(self.undeleteDestination):
            dirpath = dirpath.decode('utf-8')
            for f in files:
                logger.debug('File "%s" found.' % f)
                if not isinstance(f,unicode):
                    f = f.decode('utf-8')
                yield(os.path.join(dirpath,f))
                
    def listEmails(self):
        """
        Return the extracted mails files (even metadata files.)
        We have to append more maildirs like outlook express extractions ...
        """
        maildirs = []
        outlookMailDir = unicode(os.path.join('.frit/extractions/emails/outlook',self.evidence.configName,self.configName))
        maildirs.append(outlookMailDir)
        for md in maildirs:
            for dirpath, dirs, files in os.walk(md):
                dirpath = dirpath.decode('utf-8')
                for f in files:
                    if not isinstance(f,unicode):
                        f = f.decode('utf-8')
                    yield(os.path.join(dirpath,f))

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

    def dbCountExtension(self, ext):
        """
        A function to count a specified extension found on the filesystem
        """
        toReturn = {}
        fso =  self.getFsDb()
        fq = fritModel.File.query.filter(fritModel.File.filesystem==fso)
        fq = fq.filter(fritModel.File.state.has(state=u'Normal'))
        fq = fq.filter(fritModel.File.extension.has(extension=ext))
        nb = fq.count()
        size = 0
        if nb > 0:
            size=fq.value(func.sum(fritModel.File.filesize))
        toReturn['count'] = nb
        toReturn['size'] = size
        return toReturn

    def dbCountFiles(self):
        """
        A function to get a count of files belonging to the filesystem
        """
        toReturn = {}
        fsDb = self.getFsDb()
        for fstate in fritModel.FILESTATES:
            nbFiles = fritModel.elixir.session.query(fritModel.File).filter(fritModel.File.filesystem==fsDb)
            nbFiles = nbFiles.filter(fritModel.File.state.has(state=fstate)).count()
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

    def undelete(self):
        pass

class NtfsFileSystem(FileSystem):
    """
    Class for the NTFS file system.
    """
    def getFormat(self):
        return "NTFS"

    def mountCommand(self):
        logger.info('NTFS mounting "%s" on "%s"' % (self.loopDevice,self.fsMountPoint))
        fritutils.fritmount.ntfs3gMount(self.loopDevice,self.fsMountPoint)

    def umountCommand(self):
        logger.info('NTFS unmounting "%s"' % self.fsMountPoint)
        fritutils.fritmount.fuserUnmount(self.fsMountPoint)
       
    def undelete(self):
        """
        A function to undelete files on NTFS
        """
        self.makeUndelDir()
        self.mount('undelete','Used by ntfsundelete')
        fritutils.fritundelete.NtfsUndelete(self.loopDevice,self.undeleteDestination)
        self.umount('undelete')

class FatFileSystem(FileSystem):
    """
    Class for the FAT file system.
    """
    def getFormat(self):
        return "FAT"

    def mountCommand(self):
        logger.info('FAT mounting "%s" on "%s"' % (self.loopDevice,self.fsMountPoint))
        fritutils.fritmount.fatMount(self.loopDevice,self.fsMountPoint)
    
    def umountCommand(self):
        logger.info('FAT unmounting "%s"' % self.fsMountPoint)
        fritutils.fritmount.fatUnmount(self.fsMountPoint)

class HfsPlusFileSystem(FileSystem):
    """
    Class for the HFS+ file system.
    """
    def getFormat(self):
        return "HFSPLUS"

    def mountCommand(self):
        logger.info('HFSPLUS mounting "%s" on "%s"' % (self.loopDevice,self.fsMountPoint))
        fritutils.fritmount.hfsplusMount(self.loopDevice,self.fsMountPoint)
    
    def umountCommand(self):
        logger.info('HFSPLUS unmounting "%s"' % self.fsMountPoint)
        fritutils.fritmount.hfsplusUnmount(self.fsMountPoint)

class ISO9660FileSystem(FileSystem):
    """
    Class for the ISO 9660 file system (CDROM/DVD).
    """
    def getFormat(self):
        return "ISO9660"

    def mountCommand(self):
        fritutils.fritmount.isoMount(self.loopDevice,self.fsMountPoint)

    def umountCommand(self):
        fritutils.fritmount.fuserUnmount(self.fsMountPoint)

class Ext2FileSystem(FileSystem):
    """
    Class for the EXT 2/3 file system.
    """
    def getFormat(self):
        return "EXT2/3"

    def mountCommand(self):
        fritutils.fritmount.ext2Mount(self.loopDevice,self.fsMountPoint)

    def umountCommand(self):
        fritutils.fritmount.fuserUnmount(self.fsMountPoint)
       

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
        A function to construct the lockfile name
        """
        lockSuffix = '_' + locker + '.lock'
        return self.containerMountPoint + lockSuffix
        
    def lockList(self):
        llist = []
        lstart = len(self.containerMountPoint) + 1
        for flock in glob.glob(self.containerMountPoint + "_*.lock"):
           llist.append(flock[lstart:-5])
        return llist
        
    def lockListString(self):
        """
        Return a locklist in form of a string
        With the PID included
        """
        lstring = ''
        for l in self.lockList():
            lstring += l 
            p = ' '.join(self.getPids(l))
            lstring += ' (PIDS: ' + p + ') '
        return lstring
        
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
        llist = self.lockList()
        if locker in llist:
            return True
        else:
            return False

    def getPids(self,locker):
        pidlist = []
        lockFile = self.getLockFile(locker)
        lf = open(lockFile,'r')
        for line in lf.readlines():
            pid = line.split(': ')[1].split(' -- ')[0]
            pidlist.append(pid)
        lf.close()
        return pidlist

    def isRunning(self,locker):
        """
        Return True if at least a locker as a running PID
        """
        if not self.isLocked(locker):
            return None
        else:
            for pid in self.getPids(locker):
                procfile = os.path.join('/proc/',pid)
                if os.path.exists(procfile):
                    return True
        return False

    def isMounted(self):
        """
        Retrun true if this  is mounted
        have to be overriden by the different filesystems
        """
        pass

class DdEvidence(Evidence):
    def getFormat(self):
        return 'dd'
        
    def populateRawImage(self):
        """
        This function populate the raw image filename to all filesystems of the Evidence.
        Even if this file does not exists yet.
        """
        self.rawImage = self.fileName
        for fs in self.fileSystems:
            fs.rawImage = self.rawImage 
    
    def isMounted(self):
        # as the file exists, it like if it is always mounted
        return True

class AffEvidence(Evidence):
    def getFormat(self):
        return 'aff'
        
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
                elif fs.isMounted():
                    # Here we have an inconsistency, fs is not locked by anything but is mounted.
                    # Let's unmount it.
                    fritutils.termout.printMessage('\tUnmounting filesystems "%s" because mounted and not locked' % fs.configName)
                    fs.umount(locker)
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
    ValidFileSystems = ('FAT','NTFS','ISO9660','HFSPLUS','EXT2/3')
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
                        fs = NtfsFileSystem(offset=off,fsConfigName=subkey,evidence=ev)
                        ev.fileSystems.append(fs)
                        ev.populateRawImage()
                        if verbose:
                            fritutils.termout.printSuccess("\t\t NTFS filesystem Found at offset %d." % fs.offset)
                    elif fritConf[key][subkey]['Format'] == 'FAT':
                        off = fritutils.getOffset(fritConf[key][subkey]['Offset'])
                        fs = FatFileSystem(offset=off,fsConfigName=subkey,evidence=ev)
                        ev.fileSystems.append(fs)
                        ev.populateRawImage()
                        if verbose:
                            fritutils.termout.printSuccess("\t\t FAT filesystem Found at offset %d." % fs.offset)
                    elif fritConf[key][subkey]['Format'] == 'HFSPLUS':
                        off = fritutils.getOffset(fritConf[key][subkey]['Offset'])
                        fs = HfsPlusFileSystem(offset=off,fsConfigName=subkey,evidence=ev)
                        ev.fileSystems.append(fs)
                        ev.populateRawImage()
                        if verbose:
                            fritutils.termout.printSuccess("\t\t HFS+ filesystem Found at offset %d." % fs.offset)
                    elif fritConf[key][subkey]['Format'] == 'ISO9660':
                        off = fritutils.getOffset(fritConf[key][subkey]['Offset'])
                        fs = ISO9660FileSystem(offset=off,fsConfigName=subkey,evidence=ev)
                        ev.fileSystems.append(fs)
                        ev.populateRawImage()
                        if verbose:
                            fritutils.termout.printSuccess("\t\t ISO 9660 filesystem Found at offset %d." % fs.offset)
                    elif fritConf[key][subkey]['Format'] == 'EXT2/3':
                        off = fritutils.getOffset(fritConf[key][subkey]['Offset'])
                        fs = Ext2FileSystem(offset=off,fsConfigName=subkey,evidence=ev)
                        ev.fileSystems.append(fs)
                        ev.populateRawImage()
                        if verbose:
                            fritutils.termout.printSuccess("\t\t EXT2/3 filesystem Found at offset %d." % fs.offset)
                    elif fritConf[key][subkey]['Format'] not in ValidFileSystems:
                        fritutils.termout.printWarning("%s This filesystem type (%s) is unknow by frit." % (ev.configName,fritConf[key][subkey]['Format']))

            Evidences.append(ev)

    if len(Evidences) ==0:
        fritutils.termout.printWarning("No evidences found in config file.")
    return Evidences
