#!/usr/bin/python
"""
registry
This command is made to work on MS Windows registry files.
the "find" command will list all the registry files found.
Inspired by Harlan Carvey's RegRipper plugins.
"""

import os
import fritutils
import fritutils.fritlog
import struct
import uuid
import datetime
# Use of Will Ballenthin registry module
# https://github.com/williballenthin/python-registry
from Registry import Registry

logger = fritutils.fritlog.loggers['registryLog']

MSCLASSES = {'{53f56307-b6bf-11d0-94f2-00a0c91efb8b}': 'DISK',
             '{53f56308-b6bf-11d0-94f2-00a0c91efb8b}': 'CDROM',
             '{53f5630a-b6bf-11d0-94f2-00a0c91efb8b}': 'Partition',
             '{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}': 'Volume'
             }


class MountedDevice(object):
    """
    A class to parse monuted device entry in SYSTEM registry.
    """
    def __init__(self, name, value, registryPath):
        self.name = name
        self.value = value
        self.regpath = registryPath
        self.mountPoint = ''
        self.msType = None
        self.msDiskClass = None
        self.friendlyName = None
        self.serial = None
        self.id = None
        self.offset = None
        if len(self.value) == 12:
            self.parseTwelve()
        elif len(self.value) == 24:
            self.parseTwentyfour()
        elif '#' in self.value:
            self.parseOther()
        else:
            self.id = value
        self.searchStorage()

    def parseTwelve(self):
        mbrId = self.value[:4]
        self.id = "(MBR Id) {}".format(":".join("{:02x}".format(ord(num)) for num in mbrId))
        self.offset = struct.unpack('Q', self.value[4:])[0]/512

    def parseTwentyfour(self):
        guid = self.value[8:]
        self.id = "(GUID) {}".format(str(uuid.UUID(bytes=guid)))
        self.msType = str(self.value[:8])

    def parseOther(self):
        """
        Split based on '#' char but cannot simply split because serial may contain '#'
        """
        v = self.value
        hpos = v.find('#')
        self.msType = v[:hpos]
        v = v[hpos+1:]
        hpos = v.find('#')
        self.friendlyName = v[:hpos]
        v = v[hpos+1:]
        hpos = v.rfind('#')
        self.msDiskClass = v[hpos+1:]

        if self.msDiskClass in MSCLASSES:
            # this is not working because value is a multibyte str
            self.msDiskClass += " ({})".format(MSCLASSES[self.msDiskClass])
        else:
            self.msDiskClass += " (UNKNOWN)"
        v = v[:hpos]
        self.serial = v

    def searchStorage(self):
        """
        Searching CurentControlSet/Enum/STORAGE/Volume
        NOT WORKING RIGHT NOW
        """
        cset = getCurrentControlSet(self.regpath)
        kpath = "{}\\Enum\\Storage\\Volume".format(cset)
        reg = Registry.Registry(self.regpath)
        regRoot = reg.root()
        try:
            key = reg.open(kpath)
        except Registry.RegistryKeyNotFoundException:
            return
        for sub in key.subkeys():
            if str(sub.name()) == self.value:
                print "MATCH"


def getMSTime(lo, hi):
    """
    GetTime function from Harlan Carvey RegRipper
    translated from perl to python
    """
    if lo == 0 and hi == 0:
        t = 0
    else:
        lo -= 0xd53e8000
        hi -= 0x019db1de
        t = int(hi * 429.4967296 + lo/1e7)
    if t < 0:
        t = 0
    return t


def getKeyValueOrNone(Key, Name):
    """
    Get the value for the name entry in key Key
    or return None
    Name is a string
    Key is a Registry.Registry opened key
    """
    try:
        r = Key.value(Name).value()
    except Registry.RegistryValueNotFoundException:
        r= None
    return r


def getCurrentControlSet(sysRegPath):
    reg = Registry.Registry(sysRegPath)
    regRoot = reg.root()
    sccs = regRoot.subkey("Select")
    v = sccs.value("Current")
    return "ControlSet{:03}".format(v.value())


def find(Evidences, args):
    logger.info('Starting find subcommand.')
    for evi in Evidences:
        for fs in evi.fileSystems:
            for regfilepath in fs.getRegistryFiles():
                if regfilepath:
                    fritutils.termout.printNormal(regfilepath)
        # we have to remove the registry lock and umount its container
        if evi.isLocked('registry'):
            evi.umount('registry')


def mountDevices(Evidences, args):
    logger.info('Starting mountdevices subcommand.')
    for evi in Evidences:
        for fs in evi.fileSystems:
            fritutils.termout.printSuccess("Searching for registry files in {} {}".format(fs.evidenceConfigName, fs.configName))
            for regfilepath in fs.getRegistryFiles():
                if regfilepath and os.path.basename(regfilepath).lower() == 'system':
                    reg = Registry.Registry(regfilepath)
                    regRoot = reg.root()
                    mdk = regRoot.subkey("MountedDevices")
                    fritutils.termout.printNormal("Registry analysis of mounted devices for : {}".format(regfilepath))
                    fritutils.termout.printNormal("    MountedDevices key Timestamp: {}".format(mdk.timestamp()))
                    for v in mdk.values():
                        Device = MountedDevice(v.name(), v.value(), regfilepath)
                        fritutils.termout.printNormal("        Name: {}".format(Device.name))
                        fritutils.termout.printNormal("            Id: {}".format(Device.id))
                        if Device.msType:
                            fritutils.termout.printNormal("            MS Type: {}".format(Device.msType))
                        if Device.msDiskClass:
                            fritutils.termout.printNormal("            MS Disk Class: {}".format(Device.msDiskClass))
                        if Device.serial:
                            fritutils.termout.printNormal("            Serial: {}".format(Device.serial))
                        if Device.friendlyName:
                            fritutils.termout.printNormal("            Friendly Name: {}".format(Device.friendlyName))
                        if Device.offset:
                            fritutils.termout.printNormal("            Offset (in 512 bytes sectors): {}".format(Device.offset))
        # we have to remove the registry lock and umount its container
        if evi.isLocked('registry'):
            evi.umount('registry')


def winInfo(Evidences, args):
    """
    Show various Windows informations
    Should be in an object to help presenting informations in a consistent way
    Currently, informations are shown in file found order
    """
    logger.info('Starting wininfo subcommand.')
    for evi in Evidences:
        for fs in evi.fileSystems:
            fritutils.termout.printSuccess("Searching for registry files in {} {}".format(fs.evidenceConfigName, fs.configName))
            for regfilepath in fs.getRegistryFiles():
                if regfilepath and os.path.basename(regfilepath).lower() == 'system':
                    cur = getCurrentControlSet(regfilepath)
                    computerNameKey = Registry.Registry(regfilepath).open(cur + "\\Control\\ComputerName\\ComputerName")
                    fritutils.termout.printNormal("    Computer name entry found in '{}'".format(regfilepath))
                    fritutils.termout.printNormal("        Key timestamp: {}".format(computerNameKey.timestamp()))
                    fritutils.termout.printNormal("        Computer name: {}".format(getKeyValueOrNone(computerNameKey,'ComputerName')))
                    windowsKey = Registry.Registry(regfilepath).open(cur + "\\Control\\Windows")
                    fritutils.termout.printNormal("    Windows last shutdown time entry found in '{}'".format(regfilepath))
                    fritutils.termout.printNormal("        Key timestamp: {}".format(windowsKey.timestamp()))
                    shutimeRaw = getKeyValueOrNone(windowsKey,"ShutdownTime")
                    if shutimeRaw:
                        shutime = datetime.datetime.fromtimestamp(getMSTime(*struct.unpack('<LL',shutimeRaw))).isoformat()
                    else:
                        shutime = None
                    fritutils.termout.printNormal("        Last shutdown time: {}".format(shutime))
                if regfilepath and os.path.basename(regfilepath).lower() == 'software':
                    # Winlogon entries
                    winlogonKey = Registry.Registry(regfilepath).open("Microsoft\\Windows NT\\CurrentVersion\\Winlogon")
                    fritutils.termout.printNormal("    Registry WINLOGON entries found in '{}'".format(regfilepath))
                    fritutils.termout.printNormal("        Key timestamp: {}".format(winlogonKey.timestamp()))
                    fritutils.termout.printNormal("        Default username: {}".format(getKeyValueOrNone(winlogonKey,'DefaultUserName')))
                    fritutils.termout.printNormal("        Last used username: {}".format(getKeyValueOrNone(winlogonKey,'LastUsedUsername')))
                    # Windows Version
                    curverKey = Registry.Registry(regfilepath).open("Microsoft\\Windows NT\\CurrentVersion")
                    fritutils.termout.printNormal("    Registry Windows Version entries found in '{}'".format(regfilepath))
                    fritutils.termout.printNormal("        Key timestamp: {}".format(curverKey.timestamp()))
                    fritutils.termout.printNormal("        Product Name: {}".format(getKeyValueOrNone(curverKey,'ProductName')))
                    fritutils.termout.printNormal("        CSD Version: {}".format(getKeyValueOrNone(curverKey,'CSDVersion')))
                    fritutils.termout.printNormal("        Product Id: {}".format(getKeyValueOrNone(curverKey,'ProductId')))
                    fritutils.termout.printNormal("        Registered owner: {}".format(getKeyValueOrNone(curverKey,'RegisteredOwner')))
                    fritutils.termout.printNormal("        System root: {}".format(getKeyValueOrNone(curverKey,'SystemRoot')))
                    fritutils.termout.printNormal("        Path name: {}".format(getKeyValueOrNone(curverKey,'PathName')))
                    installDateRaw = getKeyValueOrNone(curverKey,"InstallDate")
                    if installDateRaw:
                        installDate = datetime.datetime.fromtimestamp(installDateRaw).isoformat()
                    else:
                        installDate = None
                    fritutils.termout.printNormal("        Install date: {}".format(installDate))
        # we have to remove the registry lock and umount its container
        if evi.isLocked('registry'):
            evi.umount('registry')


def factory(args):
    fritConfig = fritutils.getConfig()
    Evidences = fritutils.getEvidencesFromArgs(args, fritConfig)

    if args.cmd == 'find':
        find(Evidences, args)
    elif args.cmd == 'mountdevices':
        mountDevices(Evidences, args)
    elif args.cmd == 'wininfo':
        winInfo(Evidences, args)
