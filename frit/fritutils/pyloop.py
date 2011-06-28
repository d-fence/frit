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

LOOPMAJOR = 7
LOOP_CLR_FD = 0x4c01
LOOP_SET_FD	= 0x4C00

class testLoop(unittest.TestCase):
    """
    A class test for the pyloop module
    """
    
    def setUp(self):
        self.badfile = tempfile.NamedTemporaryFile()
        self.assocfile = tempfile.NamedTemporaryFile()
                
    def tearDown(self):
        self.badfile.close()
        self.assocfile.close()
    
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
        self.assertTrue(testLoop.unlink())
        
    def test_findFreeLoop(self):
        fl = findFreeLoop()
        self.assertEqual(type(fl),loopDevice)
        self.assertEqual(fl.is_loop_used(),False)
        

class loopDevice(object):
    def __init__(self,devPath):
        self.devPath = devPath
        self.devName = os.path.basename(self.devPath)
        self.sysPath = os.path.join('/sys/block/',self.devName)
        self.refresh()
        
    def refresh(self):
        self.sysBackingFile = self.getBackingFile()
        
    def getBackingFile(self):
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
        
    def unlink(self):
        self.refresh()
        if self.is_loop_used():
            with open(self.devPath,'r') as fd:
                fcntl.ioctl(fd,LOOP_CLR_FD)
            self.refresh()
            return True
        return False
        
    def link(self,BackingFile):
        self.refresh()
        if not self.is_loop_used():
            with open(self.devPath,'r') as fd:
                fdBackingFile = open(BackingFile,'r')
                fcntl.ioctl(fd,LOOP_SET_FD,fdBackingFile.fileno())
                fdBackingFile.close()
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
