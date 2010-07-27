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

AFFMOUNT = '/usr/bin/affuse'
FUSERMOUNT = '/usr/bin/fusermount'
NTFS3G = '/usr/bin/ntfs-3g'
LOSETUP = '/sbin/losetup'
SUDO = '/usr/bin/sudo'
MOUNT = '/bin/mount'
UMOUNT = '/bin/umount'

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
        raise fritMountError('afmount failed with file "%s" on mount point "%s" (return code: %d) ' % (affFile,mountpoint,afmount.returncode))
    elif afmount.returncode < 0:
        raise fritMountError('afmount was interupted by signal "%d"  with file "%s" on mount point "%s"' % (afmount.returncode,affFile,mountpoint))
    
def fuserUnmount(mountpoint):
    fritutils.termout.printMessage('\tUnmounting "%s"' % mountpoint)
    # we check if it's really mounted first
    if os.path.ismount(mountpoint):
        fuserunmount = subprocess.Popen([FUSERMOUNT,'-u',mountpoint])
        fuserunmount.wait()
        if fuserunmount.returncode > 0:
            raise fritMountError('Unable to unmount "%s" (return code: %d)' % (mountpoint,fuserunmount.returncode))

def fatUnmount(mountpoint):
    fritutils.termout.printMessage('\tUnmounting "%s"' % mountpoint)
    # we check if it's really mounted first
    if os.path.ismount(mountpoint):
        fatunmount = subprocess.Popen([SUDO,UMOUNT,mountpoint])
        fatunmount.wait()
        if fatunmount.returncode > 0:
            raise fritMountError('Unable to unmount "%s" (return code: %d)' % (mountpoint,fatunmount.returncode))

def attachLoopDevice(rawfile, offset):
    fritutils.termout.printMessage('\tAttaching "%s" to a loop device.' % rawfile)    
    losetup = subprocess.Popen([LOSETUP, '-f', '-r', '-o', str(offset),rawfile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    losetup.wait()
    if losetup.returncode > 0:
        raise fritMountError('Unable to attach loop device to "%s" with offset "%d".' % (rawfile,offset))
        
def detachLoopDevice(loopdev):
    fritutils.termout.printMessage('\tDetaching loop device "%s"' % loopdev)
    losetup = subprocess.Popen([LOSETUP, '-d', loopdev], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    losetup.wait()
    if losetup.returncode > 0:
        raise fritMountError('Unable to detach loop device "%s" (return code: %d)' % (loopdev, losetup.returncode))

def getLoopDevice(rawfile):
    logetdevice = subprocess.Popen([LOSETUP, '-j', rawfile],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logetdevice.wait()
    if logetdevice.returncode > 0:
        raise fritMountError('Unable to get loop informations about : %s' % rawfile)
    lodevice,stderr = logetdevice.communicate()
    if '/dev/loop' in lodevice:
        return lodevice.split()[0][0:-1]
    else:
        return ''

def ntfs3gMount(loopDevice,mountpoint):
    fritutils.termout.printMessage('\tMounting "%s" with NTFS-3G on "%s"' % (loopDevice,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = 'ro,noatime,show_sys_files,allow_other,uid=' + uid + ',gid=' + gid
    ntfsmount = subprocess.Popen([NTFS3G, '-o', options, loopDevice, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ntfsmount.wait()
    if ntfsmount.returncode > 0:
        raise fritMountError('Unable to mount the ntfs partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(ntfsmount.returncode)))

def fatMount(loopDevice,mountpoint):
    fritutils.termout.printMessage('\tMounting "%s" with FAT on "%s"' % (loopDevice,mountpoint))
    uid = str(os.getuid())
    gid = str(os.getgid())
    options = 'ro,noatime,uid=' + uid + ',gid=' + gid
    fatmount = subprocess.Popen([SUDO, MOUNT, '-t','vfat', '-o', options, loopDevice, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    fatmount.wait()
    if fatmount.returncode > 0:
        raise fritMountError('Unable to mount the FAT partition "%s" on "%s" (error %s)' % (mountpoint, loopDevice, str(fatmount.returncode)))