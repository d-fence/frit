#!/usr/bin/python
"""
registry
This command is made to work on MS Windows registry files.
the "find" command will list all the registry files found.
"""

import os
import fritutils
import fritutils.fritlog
import struct
import uuid
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


def getCurrentControlSet(sysRegPath):
    reg = Registry.Registry(sysRegPath)
    regRoot = reg.root()
    sccs = regRoot.subkey("Select")
    v = sccs.value("Current")
    return "ControlSet{:03}".format(v.value())

def find(Evidences, args, options):
    logger.info('Starting find subcommand.')
    for evi in Evidences:
        for fs in evi.fileSystems:
            for regfilepath in fs.getRegistryFiles():
                if regfilepath:
                    fritutils.termout.printNormal(regfilepath)


def mountDevices(Evidences, args, options):
    logger.info('Starting mountdevices subcommand.')
    for evi in Evidences:
        for fs in evi.fileSystems:
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


def factory(Evidences, args, options):
    if args and 'find' in args:
        args.remove('find')
        find(Evidences, args, options)
    else:
        if 'mountdevices'in  args:
            args.remove('mountdevices')
            mountDevices(Evidences, args, options)
