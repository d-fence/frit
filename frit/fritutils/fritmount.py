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

AFFMOUNT = '/usr/bin/affuse'
FUSERMOUNT = '/usr/bin/fusermount'
NTFS3G = '/usr/bin/ntfs-3g'
FUSEISO = '/usr/bin/fuseiso'
LOSETUP = '/sbin/losetup'
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
    losetup = subprocess.Popen([LOSETUP, '-v', '-f', '-r', '-o', str(offset),rawfile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    losetup.wait()
    if losetup.returncode > 0:
        logger.warning('Unable to attach loop device to "%s" with offset "%d".' % (rawfile,offset))
        raise fritMountError('Unable to attach loop device to "%s" with offset "%d".' % (rawfile,offset))
    else:
        lodevice,stderr = losetup.communicate()
        for line in lodevice.split('\n'):
            if 'Loop device is' in lodevice:
                logger.info('Loop device found and used: "%s"' % line[15:])
                return line[15:]
            else:
                logger.warning('Unable to attach loop device to "%s" with offset "%d".' % (rawfile,offset))
                raise fritMountError('Unable to attach loop device to "%s" with offset "%d".' % (rawfile,offset))
        
def detachLoopDevice(loopdev):
    fritutils.termout.printMessage('\tDetaching loop device "%s"' % loopdev)
    logger.info('Detaching loop device "%s"' % loopdev)
    losetup = subprocess.Popen([LOSETUP, '-d', loopdev], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    losetup.wait()
    if losetup.returncode > 0:
        logger.warning('Unable to detach loop device "%s" (return code: %d)' % (loopdev, losetup.returncode))
        raise fritMountError('Unable to detach loop device "%s" (return code: %d)' % (loopdev, losetup.returncode))

def verifyLoopDevice(loopdev,filename):
    """
    Function to verify if a loop device is really attached to a file.
    The command is "/sbin:losetup -j filename"
    The error code are:
    1 if the device is not configured
    2 if an error occured that prevented losetup to run correctly
    If the loop device is really attached, we return True
    If the file "filename" doesn't even exist, how could it be attached ? So we return false.
    """
    logger.info('Verifying if "%s" is attached to "%s"' % (loopdev,filename))
    answer = False
    if not os.path.exists(filename):
        return answer
    losetup = subprocess.Popen([LOSETUP, '-j', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    losetup.wait()
    if losetup.returncode > 1:
        logger.warning('losetup error for loop device "%s" (return code: %d)' % (loopdev, losetup.returncode))
        raise fritMountError('losetup error for loop device "%s" (return code: %d)' % (loopdev, losetup.returncode))
    elif losetup.returncode == 0 :
        """
        As a shortcut, we consider that the file is correctly attached if there
        We verify the the loop device returned is the one specified in the lockfile.
        """
        loresponse,stderr = losetup.communicate()
        lines = loresponse.split('\n')
        if lines:
            for line in lines:
                if len(line) > 1:
                    s = line.split(' ')
                    if len(s) > 0:
                        lodev= s[0][:-1]
                        if lodev == loopdev:
                            answer = True
    return answer

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
