#!/usr/bin/python
"""
Utilities to mount various filesystems.
Important:
- Make sure there are enough free loop devices on the system
  modify /etc/modules like:
  loop max_loop=64
- Make sure that the user can use the block devices.
  On Debian it have to belong to the 'disk' group.
- Make sure that your user can use ntfs-3g
  for example: 
  add an ntfsuser group
  make your user belonging to this group
  change the group of the ntfs-3g binary:
    sudo chown root.ntfsuser $(which ntfs-3g)
  make the ntfs-3g binary suid root and only executable by the group:
    sudo chmod 4750 $(which ntfs-3g)
"""

import subprocess
import os
import os.path
import re
import fritutils.termout
import fritutils.fritlog
import fritutils.pyloop

AFFMOUNT = '/usr/bin/affuse'
FUSERMOUNT = '/usr/bin/fusermount'
NTFS3G = '/bin/ntfs-3g'
FUSEISO = '/usr/bin/fuseiso'
SUDO = '/usr/bin/sudo'
MOUNT = '/bin/mount'
UMOUNT = '/bin/umount'
FUSEEXT2 = '/usr/bin/fuseext2'
ROFS = '/usr/bin/rofs'

logger = fritutils.fritlog.loggers['fritmountLog']

class fritMountError(Exception):
    def __init__(self,errorString):
        Exception.__init__(self)
        self.errorString = errorString

    def __str__(self):
        return repr("Fritmount Error: %s" % self.errorString)

def affMount(affFile,mountpoint):
    fritutils.termout.printMessage('\tMounting AFF file "%s" on "%s".' % (affFile,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = 'allow_other,uid=' + uid + ',gid=' + gid
    afmount = subprocess.Popen([AFFMOUNT, '-o', options, affFile, mountpoint])
    afmount.wait()
    if afmount.returncode > 0:
        logger.warning('afmount failed with file "%s" on mount point "%s" (return code: %d) ' % (affFile,mountpoint,afmount.returncode))
        raise fritMountError('afmount failed with file "%s" on mount point "%s" (return code: %d) ' % (affFile,mountpoint,afmount.returncode))
    elif afmount.returncode < 0:
        logger.warning('afmount was interupted by signal "%d"  with file "%s" on mount point "%s"' % (afmount.returncode,affFile,mountpoint))
        raise fritMountError('afmount was interupted by signal "%d"  with file "%s" on mount point "%s"' % (afmount.returncode,affFile,mountpoint))
    
def fuserUnmount(mountpoint):
    fritutils.termout.printMessage('\tUnmounting "%s"' % mountpoint)
    # we check if it's really mounted first
    if os.path.ismount(mountpoint):
        fuserunmount = subprocess.Popen([FUSERMOUNT,'-u',mountpoint])
        fuserunmount.wait()
        if fuserunmount.returncode > 0:
            logger.warning('"fusermount -u" command failed when unmounting "%s" (return code: %d)' % (mountpoint,fuserunmount.returncode))
            raise fritMountError('Unable to unmount "%s" (return code: %d)' % (mountpoint,fuserunmount.returncode))

def sudoUmount(mountpoint):
    fritutils.termout.printMessage('\tUnmounting "%s"' % mountpoint)
    # we check if it's really mounted first
    if os.path.ismount(mountpoint):
        sudounmount = subprocess.Popen([SUDO,UMOUNT,mountpoint])
        sudounmount.wait()
        if sudounmount.returncode > 0:
            logger.warning('Unable to unmount the system mounted on %s (return code: %d)' % (mountpoint,sudounmount.returncode))
            raise fritMountError('Unable to unmount "%s" (return code: %d)' % (mountpoint,sudounmount.returncode))

def fatUnmount(mountpoint):
    fritutils.termout.printMessage('\tUnmounting "%s"' % mountpoint)
    # we check if it's really mounted first
    if os.path.ismount(mountpoint):
        fatunmount = subprocess.Popen([SUDO,UMOUNT,mountpoint])
        fatunmount.wait()
        if fatunmount.returncode > 0:
            logger.warning('Unable to unmount the FAT system mounted on %s (return code: %d)' % (mountpoint,fatunmount.returncode))
            raise fritMountError('Unable to unmount "%s" (return code: %d)' % (mountpoint,fatunmount.returncode))

def hfsplusUnmount(mountpoint):
    fritutils.termout.printMessage('\tUnmounting "%s"' % mountpoint)
    # we check if it's really mounted first
    if os.path.ismount(mountpoint):
        hfsplusunmount = subprocess.Popen([SUDO,UMOUNT,mountpoint])
        hfsplusunmount.wait()
        if hfsplusunmount.returncode > 0:
            logger.warning('Unable to unmount the HFS+ system mounted on %s (return code: %d)' % (mountpoint,hfsplusunmount.returncode))
            raise fritMountError('Unable to unmount "%s" (return code: %d)' % (mountpoint,hfsplusunmount.returncode))

def attachLoopDevice(rawfile, offset):
    """
    Function to attach a loop device to a rawfile.
    Here, we count on the "verbose" mode of the losetup command to return a
    string that begin with 'Loop device is' and contains the loop device.
    Not very ellegant.
    """
    fritutils.termout.printMessage('\tAttaching "%s" to a loop device.' % rawfile)
    logger.info('Attaching "%s" to a loop device' % rawfile)
    # finding a free loop device
    lodevice = fritutils.pyloop.findFreeLoop()
    if not lodevice.link(rawfile,offset):
        logger.warning('Unable to attach loop "%s" device to "%s" with offset "%d".' % (lodevice.devPath,rawfile,offset))
        raise fritMountError('Unable to attach loop device "%s" to "%s" with offset "%d".' % (lodevice.devPath,rawfile,offset))
    else:
       logger.info('Loop device found and used: "%s"' % lodevice.devPath)
       return lodevice.devPath
        
def detachLoopDevice(loopdev):
    fritutils.termout.printMessage('\tDetaching loop device "%s"' % loopdev)
    logger.info('Detaching loop device "%s"' % loopdev)
    lodevice = fritutils.pyloop.loopDevice(loopdev)
    if not lodevice.is_loop_used():
        logger.warning('Unable to detach loop device "%s", device not in use.' % loopdev)
        raise fritMountError('Unable to detach loop device "%s", device not in use.' % loopdev)
    elif not lodevice.unlink():
        logger.warning('Unable to detach loop device "%s"' % loopdev)
        raise fritMountError('Unable to detach loop device "%s"' % loopdev)

def verifyLoopDevice(loopdev,filename):
    """
    Function to verify if a loop device is really attached to a file.
    """
    
    fpath = os.path.abspath(filename)
    
    if not os.path.exists(fpath):
        logger.warning('"%s" file does not exist and therefore, cannot be attached to loop device "%s"' % (filename,loopdev))
        return False
    
    lodevice = fritutils.pyloop.loopDevice(loopdev)
    if not lodevice.is_loop_used():
        logger.warning('Loop device "%s" is not in use and therefore, cannot be attached to file "%s"' % (loopdev,filename))
        return False
    else:
        if lodevice.sysBackingFile != fpath:
            logger.warning('Loop device "%s" is attached to "%s", not "%s"' % (loopdev,lodevice.sysBackingFile,filename))
            return False
        else:
            return True

def ntfs3gMount(loopDevice,mountpoint):
    fritutils.termout.printMessage('\tMounting "%s" with NTFS-3G on "%s"' % (loopDevice,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = 'ro,noatime,show_sys_files,allow_other,uid=' + uid + ',gid=' + gid
    ntfsmount = subprocess.Popen([NTFS3G, '-o', options, loopDevice, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ntfsmount.wait()
    if ntfsmount.returncode > 0:
        logger.warning('Unable to mount the ntfs partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(ntfsmount.returncode)))
        raise fritMountError('Unable to mount the ntfs partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(ntfsmount.returncode)))

def fatMount(loopDevice,mountpoint):
    fritutils.termout.printMessage('\tMounting "%s" with FAT on "%s"' % (loopDevice,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = 'ro,noatime,uid=' + uid + ',gid=' + gid
    fatmount = subprocess.Popen([SUDO, MOUNT, '-t','vfat', '-o', options, loopDevice, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    fatmount.wait()
    if fatmount.returncode > 0:
        logger.warning('Unable to mount the FAT partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(fatmount.returncode)))
        raise fritMountError('Unable to mount the FAT partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(fatmount.returncode)))

def hfsplusMount(loopDevice,mountpoint):
    fritutils.termout.printMessage('\tMounting "%s" with HFS+ on "%s"' % (loopDevice,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = 'ro,noatime,uid=' + uid + ',gid=' + gid
    hfsplusmount = subprocess.Popen([SUDO, MOUNT, '-t','hfsplus', '-o', options, loopDevice, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    hfsplusmount.wait()
    if hfsplusmount.returncode > 0:
        logger.warning('Unable to mount the HFS+ partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(hfsplusmount.returncode)))
        raise fritMountError('Unable to mount the HFS+ partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(hfsplusmount.returncode)))

def isoMount(loopDevice,mountpoint):
    """
    fuseiso doesn't need a loop file. We can mount the iso file directly.
    Should work on that to avoid loop devices
    """
    fritutils.termout.printMessage('\tMounting "%s" with fuseiso on "%s"' % (loopDevice,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = '-n'
    fuseoptions = 'ro,noatime,allow_other,uid=' + uid + ',gid=' + gid
    isomount = subprocess.Popen([FUSEISO, options, loopDevice, mountpoint,'-o',fuseoptions], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    isomount.wait()
    if isomount.returncode > 0:
        logger.warning('Unable to mount the ISO 9660 filesystem "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(isomount.returncode)))
        raise fritMountError('Unable to mount the ISO 9660 filesystem "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(isomount.returncode)))

def ext2Mount(loopDevice,mountpoint):
    fritutils.termout.printMessage('\tMounting "%s" with fuseext2 on "%s"' % (loopDevice,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = 'ro,noatime,allow_other,uid=' + uid + ',gid=' + gid + ',modules=iconv,from_code=UTF-8,to_code=UTF-8'
    ext2mount = subprocess.Popen([FUSEEXT2, '-o', options, loopDevice, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ext2mount.wait()
    if ext2mount.returncode > 0:
        logger.warning('Unable to mount the EXT2/3 partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(ext2mount.returncode)))
        raise fritMountError('Unable to mount the EXT2/3 partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(ext2mount.returncode)))
        
def rofsMount(directory,mountpoint):
    fritutils.termout.printMessage('\tMounting "%s" with rofs on "%s"' % (directory,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = 'ro,noatime,allow_other,uid=' + uid + ',gid=' + gid + ',modules=iconv,from_code=UTF-8,to_code=UTF-8'
    rofsmount = subprocess.Popen([ROFS, '-o', options, directory, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    rofsmount.wait()
    if rofsmount.returncode > 0:
        logger.warning('Unable to mount the ROFS directory "%s" on "%s" (error %s)' % (mountpoint, directory, str(rofsmount.returncode)))
        raise fritMountError('Unable to mount the ROFS directory "%s" on "%s" (error %s)' % (mountpoint, directory, str(rofsmount.returncode)))
