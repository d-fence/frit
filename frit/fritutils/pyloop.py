#!/usr/bin/python
"""
A module for managing loop devices
"""
import os
import stat
import fcntl
import unittest
import tempfile
import glob
import struct
import time

LOOPMAJOR = 7
LOOP_CLR_FD = 0x4c01
LOOP_SET_FD	= 0x4C00
LOOP_GET_STATUS64 = 0x4C05
LOOP_SET_STATUS64 = 0x4C04

class testLoop(unittest.TestCase):
    """
    A class test for the pyloop module
    """

    def setUp(self):
        self.badfile = tempfile.NamedTemporaryFile()
        self.assocfile = tempfile.NamedTemporaryFile(delete=False)
        self.asector = 'A' * 512
        self.bsector = 'B' * 512
        self.assocfile.write(self.asector)
        self.assocfile.write(self.bsector)
        self.assocfile.close()

    def tearDown(self):
        self.badfile.close()
        os.remove(self.assocfile.name)

    def test_is_loop_device(self):
        self.assertTrue(is_loop_device('/dev/loop0'))
        self.assertFalse(is_loop_device(self.badfile.name))

    def test_loop_class(self):
        """
        Here we try the class with the last loop device on the system in
        the hope that it's not used (strange to rely on hope in a unit test
        but I really don't know how to do it in a better way).
        """
        lodevs = glob.glob('/dev/loop*')
        lonums = []
        for lo in lodevs:
            if lo != '/dev/loop-control':
                lonum = int(lo[9:])
                lonums.append(lonum)
        lonums.sort()
        lastDev = str(lonums[-1])
        testLoop = loopDevice('/dev/loop' + lastDev)
        self.assertEqual(testLoop.getBackingFile(),None)
        self.assertFalse(testLoop.is_loop_used())
        self.assertEqual(testLoop.sysBackingFile,None)
        self.assertTrue(testLoop.link(self.assocfile.name))
        self.assertTrue(testLoop.is_loop_used())
        self.assertEqual(testLoop.getBackingFile(),self.assocfile.name)
        with open(testLoop.devPath,'r') as ldfile:
            x = ldfile.read(512)
        self.assertEqual(x,self.asector)
        self.assertTrue(testLoop.unlink())
        self.assertFalse(testLoop.is_loop_used())

        self.assertTrue(testLoop.link(self.assocfile.name,512))
        self.assertTrue(testLoop.is_loop_used())
        self.assertEqual(testLoop.getBackingFile(),self.assocfile.name)
        self.assertTrue(testLoop.get_infos())

        s = os.stat(self.assocfile.name)
        inode = s.st_ino
        dev = s.st_dev

        self.assertTrue(testLoop.infos.DeviceNum,dev)
        self.assertTrue(testLoop.infos.Inode,inode)

        with open(testLoop.devPath,'r') as ldfile:
            x = ldfile.read(512)
        self.assertEqual(x,self.bsector)

        self.assertEqual(testLoop.infos.BackingFile,testLoop.sysBackingFile)
        self.assertEqual(testLoop.infos.Offset,512)

        self.assertTrue(testLoop.unlink())
        self.assertFalse(testLoop.is_loop_used())
        self.assertFalse(testLoop.get_infos())

        # now testing sizelimit
        self.assertTrue(testLoop.link(self.assocfile.name,0,512))
        with open(testLoop.devPath,'r') as ldfile:
            x = ldfile.read()
        self.assertEqual(x,self.asector)
        self.assertTrue(testLoop.unlink())

    def test_Raise(self):
        self.assertRaises(LoopException,loopDevice,self.assocfile.name)

    def test_findFreeLoop(self):
        fl = findFreeLoop()
        self.assertEqual(type(fl),loopDevice)
        self.assertEqual(fl.is_loop_used(),False)

class LoopException(Exception):
       def __init__(self, msg):
           self.msg = msg
       def __str__(self):
           return repr(self.msg)

class loopInfos(object):
    def __init__(self):
        self.infoList = None
        self.infoStruct = '\0' * 232
        self.BackingFile = None
        self.Offset = 0
        self.Sizelimit = 0
        self.unpack()
    
    def _listToObject(self):
        """
        This structure can only hold the 64 first bytes of 
        the backing file name. It's better to rely on sysfs to get the
        backing file name
        """
        self.DeviceNum = self.infoList[0]
        self.Inode = self.infoList[1]
        self.Offset = self.infoList[3]
        self.Sizelimit = self.infoList[4]
        self.BackingFile = self.infoList[9].strip('\0')
    
    def _objectToList(self):
        self.infoList[3] = self.Offset
        self.infoList[4] = self.Sizelimit
        self.infoList[9] = self.BackingFile
    
    def unpack(self):
        self.infoList = list(struct.unpack('LLLLLIIII64s64s32sLL',self.infoStruct))
        self._listToObject()
        
    def pack(self):
        self._objectToList()
        self.infoStruct = struct.pack('LLLLLIIII64s64s32sLL',*self.infoList)

class loopDevice(object):
    def __init__(self,devPath):
        if not is_loop_device(devPath):
            raise LoopException("'%s' is not a loop device" % devPath)
        self.devPath = devPath
        self.devName = os.path.basename(self.devPath)
        self.sysPath = os.path.join('/sys/block/',self.devName)
        self.infos = loopInfos()
        self.refresh()

    def refresh(self):
        self.sysBackingFile = self.getBackingFile()

    def getBackingFile(self):
        """
        This function return the name of the file linked to the loop device.
        The user should rely on this function instead than relying on the 
        sysBackingFile object attriubute that may not be up to date.
        """
        sbpath = os.path.join(self.sysPath,'loop/backing_file')
        if os.path.exists(sbpath):
            with open(sbpath,'r') as fb:
                bf = fb.readline().strip()
        else:
            bf = None
        return bf

    def is_loop_used(self):
        self.refresh()
        if self.sysBackingFile and os.path.exists(self.sysBackingFile):
            return True
        return False

    def get_infos(self):
        self.refresh()
        # we need to initialize infos, otherwise we can have old ifos if
        # loop device is not mounted anymore
        self.infos = loopInfos()
        if self.is_loop_used():
            with open(self.devPath,'r') as fd:
                self.infos.infoStruct = fcntl.ioctl(fd,LOOP_GET_STATUS64,self.infos.infoStruct)
                self.infos.unpack()
            return True
        return False

    def unlink(self):
        self.refresh()
        if self.is_loop_used():
            with open(self.devPath,'r') as fd:
                """
                Sometimes, the device is busy and we have to wait a second
                before retrying to detach, maximum 3 times.
                """
                for i in range(3):
                    try:
                        fcntl.ioctl(fd,LOOP_CLR_FD)
                        unlinked = True
                        break
                    except IOError:
                        if i == 2:
                            raise
                        time.sleep(1)
            self.refresh()
            self.infos = loopInfos()
            return True
        return False

    def link(self,BackingFile,Offset=0,Sizelimit=0):
        self.refresh()
        if not self.is_loop_used():
            with open(self.devPath,'w') as fd:
                fdBackingFile = open(BackingFile,'r')
                fcntl.ioctl(fd,LOOP_SET_FD,fdBackingFile.fileno())
                fdBackingFile.close()
                self.infos.BackingFile = BackingFile
                self.infos.Offset = Offset
                self.infos.Sizelimit = Sizelimit
                self.infos.pack()
                self.infos.infoStruct = fcntl.ioctl(fd,LOOP_SET_STATUS64,self.infos.infoStruct)
                self.infos.unpack()
            self.refresh()
            return True
        return False

def is_loop_device(devPath):
    """
    test if a device is really a loop device
    >>> is_loop_device('/dev/loop0')
    True
    """
    info = os.stat(devPath)
    if stat.S_ISBLK(info.st_mode):
        if os.major(info.st_rdev) == LOOPMAJOR:
            return True
    return False

def findFreeLoop():
    """
    Find a free loop device if any
    and return a loopDevice instance
    """
    for lodev in glob.glob('/dev/loop*'):
        if is_loop_device(lodev):
            l = loopDevice(lodev)
            if not l.is_loop_used():
                return l
    return None

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main()
