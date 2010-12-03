#!/usr/bin/python
"""
A module to try to detect filesystems that are lying on a media.
This module is largely inspired by disktype from Christoph Pfisterer.
"""
import sys
import struct

# A class for minimal Filsystem description
# a position in bytes from begining of file
# a name
class FileSystem(object):
    def __init__(self,position=None, name=None):
        self.position = position
        self.name = name

    def setPosition(self,position):
        self.position = position

DosSystypes = {
   0x00: "Empty" ,
   0x01: "FAT12" ,
   0x02: "XENIX root" ,
   0x03: "XENIX usr" ,
   0x04: "FAT16 <32M" ,
   0x05: "Extended" ,
   0x06: "FAT16" ,
   0x07: "HPFS/NTFS" ,
   0x08: "AIX" ,
   0x09: "AIX bootable" ,
   0x0a: "OS/2 Boot Manager" ,
   0x0b: "Win95 FAT32" ,
   0x0c: "Win95 FAT32 (LBA)" ,
   0x0e: "Win95 FAT16 (LBA)" ,
   0x0f: "Win95 Ext'd (LBA)" ,
   0x10: "OPUS" ,
   0x11: "Hidden FAT12" ,
   0x12: "Compaq diagnostics" ,
   0x14: "Hidden FAT16 <32M" ,
   0x16: "Hidden FAT16" ,
   0x17: "Hidden HPFS/NTFS" ,
   0x18: "AST SmartSleep" ,
   0x1b: "Hidden Win95 FAT32" ,
   0x1c: "Hidden Win95 FAT32 (LBA)" ,
   0x1e: "Hidden Win95 FAT16 (LBA)" ,
   0x24: "NEC DOS" ,
   0x39: "Plan 9" ,
   0x3c: "PartitionMagic recovery" ,
   0x40: "Venix 80286" ,
   0x41: "PPC PReP Boot" ,
   0x42: "SFS / MS LDM" ,
   0x4d: "QNX4.x" ,
   0x4e: "QNX4.x 2nd part" ,
   0x4f: "QNX4.x 3rd part" ,
   0x50: "OnTrack DM" ,
   0x51: "OnTrack DM6 Aux1" ,
   0x52: "CP/M" ,
   0x53: "OnTrack DM6 Aux3" ,
   0x54: "OnTrackDM6" ,
   0x55: "EZ-Drive" ,
   0x56: "Golden Bow" ,
   0x5c: "Priam Edisk" ,
   0x61: "SpeedStor" ,
   0x63: "GNU HURD or SysV" ,
   0x64: "Novell Netware 286" ,
   0x65: "Novell Netware 386" ,
   0x70: "DiskSecure Multi-Boot" ,
   0x75: "PC/IX" ,
   0x78: "XOSL" ,
   0x80: "Old Minix" ,
   0x81: "Minix / old Linux" ,
   0x82: "Linux swap / Solaris" ,
   0x83: "Linux" ,
   0x84: "OS/2 hidden C: drive" ,
   0x85: "Linux extended" ,
   0x86: "NTFS volume set" ,
   0x87: "NTFS volume set" ,
   0x8e: "Linux LVM" ,
   0x93: "Amoeba" ,
   0x94: "Amoeba BBT" ,
   0x9f: "BSD/OS" ,
   0xa0: "IBM Thinkpad hibernation" ,
   0xa5: "FreeBSD" ,
   0xa6: "OpenBSD" ,
   0xa7: "NeXTSTEP" ,
   0xa9: "NetBSD" ,
   0xaf: "Mac OS X" ,
   0xb7: "BSDI fs" ,
   0xb8: "BSDI swap" ,
   0xbb: "Boot Wizard hidden" ,
   0xc1: "DRDOS/sec (FAT-12)" ,
   0xc4: "DRDOS/sec (FAT-16 < 32M)" ,
   0xc6: "DRDOS/sec (FAT-16)" ,
   0xc7: "Syrinx" ,
   0xda: "Non-FS data" ,
   0xdb: "CP/M / CTOS / ..." ,
   0xde: "Dell Utility" ,
   0xdf: "BootIt" ,
   0xe1: "DOS access" ,
   0xe3: "DOS R/O" ,
   0xe4: "SpeedStor" ,
   0xeb: "BeOS fs" ,
   0xee: "EFI GPT protective" ,
   0xef: "EFI System (FAT)" ,
   0xf0: "Linux/PA-RISC boot" ,
   0xf1: "SpeedStor" ,
   0xf4: "SpeedStor" ,
   0xf2: "DOS secondary" ,
   0xfd: "Linux raid autodetect" ,
   0xfe: "LANstep" ,
   0xff: "BBT"
}

def getBuffer(fname,pos,size):
    """
    Get a buffer from a filename starting at position pos
    with a size of size.
    """
    # should check if file exists first and what kind of filename
    fic = open(fname,"rb")
    fic.seek(pos)
    buf = fic.read(size)
    fic.close()
    return buf

def detectFat(buf):
    fatNames = ('FAT12', 'FAT16', 'FAT32')
    allowedSectSizes = ( 512, 1024, 2048, 4096 )
    # first we check the sector size like said in disktype
    sectsize = struct.unpack('H', buf[11:13])[0]
    if sectsize not in allowedSectSizes:
        return None
    # now we check sectors per cluster that must be a power of two
    clustersize = struct.unpack('B', buf[13])[0]
    if clustersize == 0 or (clustersize & (clustersize - 1)) != 0:
        return None
    # Now we check if it's not NTFS
    if buf[3:11] == "NTFS    ":
        return None

    # Now it's time to use the score system of disktype
    score = 0
    # boot jump
    if ord(buf[0]) == 0xEB and ord(buf[2]) == 0x90 or ord(buf[0]) == 0xE9:
        score += 1
    # boot signature
    if ord(buf[510]) == 0x55 and ord(buf[511]) == 0xAA:
        score += 1
    # reserved sectors
    reserved = struct.unpack('B', buf[14])[0]
    if reserved == 1 or reserved == 32:
        score +=1

    # number of FATS
    fatcount = struct.unpack('B', buf[16])[0]
    if fatcount == 2:
        score += 1
    # media byte
    if ord(buf[21]) == 0xF0 or ord(buf[21]) >= 0xF8:
        score += 1

    if score > 2:
        foundfs = FileSystem(name="FAT")
        return foundfs
    else:
        return None

def detectNtfs(buf):
    if buf[3:11] != "NTFS    ":
        return None
    # sector size: must be a power of two
    sectsize = struct.unpack('H',buf[11:13])[0]
    if sectsize < 512 or (sectsize & (sectsize - 1)) != 0:
        return None
    # sectors per cluster: must be a power of two
    clustersize = struct.unpack('B',buf[13])[0]
    if clustersize == 0 or (clustersize & (clustersize - 1)) != 0:
        return None

    fs = FileSystem(name="NTFS")
    return fs

def detectIso9660(buf):
    if buf[32769:32774] != "CD001":
        return None
    # NSR0 means UDF filesystem
    if buf[38913:38917] == "NSR0":
        return None
    
    fs = FileSystem(name="ISO9660")
    return fs
    

def detectFs(fname,position):
    buf = getBuffer(fname, position, 512)
    fs = detectFat(buf)
    if fs:
        fs.setPosition(position)
        return fs
    fs = detectNtfs(buf)
    if fs:
        fs.setPosition(position)
        return fs
    
    buf = getBuffer(fname, position, 39424)
    fs = detectIso9660(buf)
    if fs:
        fs.setPosition(position)
        return fs

def checkDosSignature(buf):
    if ord(buf[510]) != 0x55 or ord(buf[511]) != 0xAA:
        return False
    return True

def detectExtended(fname,position,previous):
    """
    Detect DOS Extended Partition Mapping
    """
    fsList = []
    xxx = []

    buf = getBuffer(fname,position,512)
    if len(buf) < 512:
        return None

    #check signature
    if not checkDosSignature(buf):
        return None

    # Get the essential informations about the 4 primary partitions
    offset = 446
    for i in range(0,4):
        ty = ord(buf[offset + 4])
        partType = DosSystypes[ty]
        # We assume that sector size is always 512 bytes
        fsStart =  struct.unpack('I',buf[offset + 8:offset + 12])[0] * 512
        partSize = struct.unpack('I',buf[offset + 12:offset+16])[0] * 512
        offset += 16
        if fsStart > 0:
            # If we have an inner extended partition, we have to recurse
            if ty == 0x05 or ty == 0x85:
                xxx = detectExtended(fname,fsStart + position - previous, fsStart)
                fsList.extend(xxx)
            else:
                fs = detectFs(fname,fsStart + position)
                if fs:
                    fsList.append(fs)

    return fsList

def detectDosMap(fname,buf):
    """
    Detect DOS Partition Mapping
    """
    FileSystems = []
    # check if buf is able to contain a DOS partition map
    if len(buf) < 512:
        return FileSystems

    # Check signature
    if not checkDosSignature(buf):
        return FileSystems

    # Get the essential informations about the 4 primary partitions
    offset = 446
    for i in range(0,4):
        ty = ord(buf[offset + 4])
        if ty in DosSystypes.keys():
            partType = DosSystypes[ty]
        else:
            partType = ''
        # We assume that sector size is always 512 bytes
        fsStart =  struct.unpack('I',buf[offset + 8:offset + 12])[0] * 512
        partSize = struct.unpack('I',buf[offset + 12:offset+16])[0] * 512
        offset += 16
        if fsStart > 0:
            if ty == 0x05 or ty == 0x0f or ty == 0x85:
                fss = detectExtended(fname,fsStart,0)
                if fss:
                    FileSystems.extend(fss)
            else:
                fs = detectFs(fname,fsStart)
                if fs:
                    FileSystems.append(fs)
    return FileSystems

def getFileSystems(fname):
    FileSystems = []
    buf = getBuffer(fname,0,512)
    FileSystems = detectDosMap(fname,buf)
    # If there is no partitioning, we try to discover a filesystem alone at the
    # begining of the file.
    if len(FileSystems) == 0:
        fs = detectFs(fname, 0)
        if fs:
            FileSystems.append(fs)
        return FileSystems
    else:
        return FileSystems

if __name__ == '__main__':
    fname = sys.argv[1]
    fl = getFileSystems(fname)
    if fl:
        for fs in fl:
            print fs.name, fs.position

