#!/usr/bin/python
"""
A module to try to detect filesystems that are lying on a media.
This module is largely inspired by disktype from Christoph Pfisterer.
"""
import sys
import struct
import uuid
import fritutils.termout

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

# GUID of partition types from wikipedia
GuidPartTypes = {
    "024dee41-33e7-11d3-9d69-0008c781f39f": "MBR partition scheme",
    "c12a7328-f81f-11d2-ba4b-00a0c93ec93b": "EFI System partition",
    "21686148-6449-6e6f-744e-656564454649": "BIOS Boot partition[e]",
    "d3bfe2de-3daf-11df-ba40-e3a556d89593": "Intel Fast Flash (iFFS) partition (for Intel Rapid Start technology)",
    "f4019732-066e-4e12-8273-346c5641494f": "Sony boot partition",
    "bfbfafe7-a34f-448a-9a5b-6213eb736c22": "Lenovo boot partition",
    "e3c9e316-0b5c-4db8-817d-f92df00215ae": "Microsoft Reserved Partition (MSR)",
    "ebd0a0a2-b9e5-4433-87c0-68b6b72699c7": "Basic data partition",
    "5808c8aa-7e8f-42e0-85d2-e1e90434cfb3": "Logical Disk Manager (LDM) metadata partition",
    "af9b60a0-1431-4f62-bc68-3311714a69ad": "Logical Disk Manager data partition",
    "de94bba4-06d1-4d40-a16a-bfd50179d6ac": "Windows Recovery Environment",
    "37affc90-ef7d-4e96-91c3-2d7ae055b174": "IBM General Parallel File System (GPFS) partition",
    "e75caf8f-f680-4cee-afa3-b001e56efc2d": "Storage Spaces partition",
    "75894c1e-3aeb-11d3-b7c1-7b03a0000000": "Data partition",
    "e2a1e728-32e3-11d6-a682-7b03a0000000": "Service Partition",
    "0fc63daf-8483-4772-8e79-3d69d8477de4": "Linux filesystem data",
    "a19d880f-05fc-4d3b-a006-743f0f84911e": "RAID partition",
    "0657fd6d-a4ab-43c4-84e5-0933c84b4f4f": "Swap partition",
    "e6d6d379-f507-44c2-a23c-238f2a3df928": "Logical Volume Manager (LVM) partition",
    "933ac7e1-2eb4-4f13-b844-0e14e2aef915": "/home partition[26]",
    "3b8f8425-20e0-4f3b-907f-1a25a76f98e8": "/srv (server data) partition",
    "7ffec5c9-2d00-49b7-8941-3ea10a5586b7": "Plain dm-crypt partition",
    "ca7d7ccb-63ed-4c53-861c-1742536059cc": "LUKS partition",
    "8da63339-0007-60c0-c436-083ac8230908": "Reserved",
    "83bd6b9d-7f41-11dc-be0b-001560b84f0f": "Boot partition",
    "516e7cb4-6ecf-11d6-8ff8-00022d09712b": "Data partition",
    "516e7cb5-6ecf-11d6-8ff8-00022d09712b": "Swap partition",
    "516e7cb6-6ecf-11d6-8ff8-00022d09712b": "Unix File System (UFS) partition",
    "516e7cb8-6ecf-11d6-8ff8-00022d09712b": "Vinum volume manager partition",
    "516e7cba-6ecf-11d6-8ff8-00022d09712b": "ZFS partition",
    "48465300-0000-11aa-aa11-00306543ecac": "Hierarchical File System Plus (HFS+) partition",
    "55465300-0000-11aa-aa11-00306543ecac": "Apple UFS",
    "6a898cc3-1dd2-11b2-99a6-080020736631": "ZFS",
    "52414944-0000-11aa-aa11-00306543ecac": "Apple RAID partition",
    "52414944-5f4f-11aa-aa11-00306543ecac": "Apple RAID partition offline",
    "426f6f74-0000-11aa-aa11-00306543ecac": "Apple Boot partition",
    "4c616265-6c00-11aa-aa11-00306543ecac": "Apple Label",
    "5265636f-7665-11aa-aa11-00306543ecac": "Apple TV Recovery partition",
    "53746f72-6167-11aa-aa11-00306543ecac": "Apple Core Storage (i.e. Lion FileVault) partition",
    "6a82cb45-1dd2-11b2-99a6-080020736631": "Boot partition",
    "6a85cf4d-1dd2-11b2-99a6-080020736631": "Root partition",
    "6a87c46f-1dd2-11b2-99a6-080020736631": "Swap partition",
    "6a8b642b-1dd2-11b2-99a6-080020736631": "Backup partition",
    "6a898cc3-1dd2-11b2-99a6-080020736631": "/usr partition",
    "6a8ef2e9-1dd2-11b2-99a6-080020736631": "/var partition",
    "6a90ba39-1dd2-11b2-99a6-080020736631": "/home partition",
    "6a9283a5-1dd2-11b2-99a6-080020736631": "Alternate sector",
    "6a945a3b-1dd2-11b2-99a6-080020736631": "Reserved partition",
    "6a9630d1-1dd2-11b2-99a6-080020736631": "Reserved partition",
    "6a980767-1dd2-11b2-99a6-080020736631": "Reserved partition",
    "6a96237f-1dd2-11b2-99a6-080020736631": "Reserved partition",
    "6a8d2ac7-1dd2-11b2-99a6-080020736631": "Reserved partition",
    "49f48d32-b10e-11dc-b99b-0019d1879648": "Swap partition",
    "49f48d5a-b10e-11dc-b99b-0019d1879648": "FFS partition",
    "49f48d82-b10e-11dc-b99b-0019d1879648": "LFS partition",
    "49f48daa-b10e-11dc-b99b-0019d1879648": "RAID partition",
    "2db519c4-b10f-11dc-b99b-0019d1879648": "Concatenated partition",
    "2db519ec-b10f-11dc-b99b-0019d1879648": "Encrypted partition",
    "fe3a2a5d-4f32-41a7-b725-accc3285a309": "ChromeOS kernel",
    "3cb8e202-3b7e-47dd-8a3c-7ff2a13cfcec": "ChromeOS rootfs",
    "2e0a753d-9e48-43b0-8337-b15192cb1b5e": "ChromeOS future use",
    "42465331-3ba3-10f1-802a-4861696b7521": "Haiku BFS",
    "85d5e45e-237c-11e1-b4b3-e89a8f7fc3a7": "Boot partition",
    "85d5e45a-237c-11e1-b4b3-e89a8f7fc3a7": "Data partition",
    "85d5e45b-237c-11e1-b4b3-e89a8f7fc3a7": "Swap partition",
    "0394ef8b-237e-11e1-b4b3-e89a8f7fc3a7": "Unix File System (UFS) partition",
    "85d5e45c-237c-11e1-b4b3-e89a8f7fc3a7": "Vinum volume manager partition",
    "85d5e45d-237c-11e1-b4b3-e89a8f7fc3a7": "ZFS partition",
    "45b0969e-9b03-4f30-b4c6-b4b80ceff106": "Ceph Journal",
    "45b0969e-9b03-4f30-b4c6-5ec00ceff106": "Ceph dm-crypt Encrypted Journal",
    "4fbd7e29-9d25-41b8-afd0-062c0ceff05d": "Ceph OSD",
    "4fbd7e29-9d25-41b8-afd0-5ec00ceff05d": "Ceph dm-crypt OSD",
    "89c57f98-2fe5-4dc0-89c1-f3ad0ceff2be": "Ceph disk in creation",
    "89c57f98-2fe5-4dc0-89c1-5ec00ceff2be": "Ceph dm-crypt disk in creation",
    "824cc7a0-36a8-11e3-890a-952519ad3f61": "Data partition",
    "cef5a9ad-73bc-4601-89f3-cdeeeee321a1": "Power-safe (QNX6) file system",
    "c91818f9-8025-47af-89d2-f030d7000c2c": "Plan 9 partition",
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
    # If the buffer is , we probably tried to read beyond the limits
    # So it's probably an length calculation that is wrong.
    # We assume that we have to stop searching here
    if len(buf) == 0:
        return None
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
        fritutils.termout.printSuccess("MBR Partition of type '{}' found".format(partType))
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


def detectGPT(fname):
    """
    Detect GPT
    We should be carefull for sector size
    """
    FileSystems = []
    buf = getBuffer(fname,0,512)
    if len(buf) < 512:
        return FileSystems
    mbrtype = ord(buf[450])
    if mbrtype == 0xee:
        fritutils.termout.printSuccess("Protective MBR found")
    else:
        return FileSystems

    fritutils.termout.printSuccess("Reading GPT")
    buf = getBuffer(fname,512,512)
    efiSignature = buf[:8]
    if efiSignature != 'EFI PART':
        fritutils.termout.printWarning("Bad EFI Signature: {}".format(efiSignature))
        return FileSystems
    lbaTable = struct.unpack('Q', buf[72:80])[0]
    nbDescriptors = struct.unpack('I', buf[80:84])[0]
    sizeDescriptors = struct.unpack('I', buf[84:88])[0]
    fritutils.termout.printSuccess("GPT is at LBA {}".format(lbaTable))
    fritutils.termout.printSuccess("    Number of entries in GPT: {}".format(nbDescriptors))
    fritutils.termout.printSuccess("    Entries sizes: {}".format(sizeDescriptors))
    buf = getBuffer(fname, 512*lbaTable, 512*32)
    for i in range(0,128):
        entryStart = i * sizeDescriptors
        entryEnd = entryStart + sizeDescriptors
        bufEntry = buf[entryStart:entryEnd]
        guidType = uuid.UUID(bytes_le=bufEntry[:16])
        if str(guidType) in GuidPartTypes:
            partTypeName = GuidPartTypes[str(guidType)]
        else:
            partTypeName = "Unknown"
        guidPart = uuid.UUID(bytes_le=bufEntry[16:32])
        lbaStart = struct.unpack('Q', bufEntry[32:40])[0]
        lbaEnd = struct.unpack('Q', bufEntry[40:48])[0]
        partSize = (lbaEnd - lbaStart) * 512
        if lbaStart == 0 and lbaEnd == 0 and str(guidType) == '00000000-0000-0000-0000-000000000000':
            break
        nameEndPos = bufEntry[56:].find('\x00\x00') + 1
        partName = bufEntry[56:56+nameEndPos].decode('utf-16le')
        fritutils.termout.printSuccess("        GPT entry {}:".format(i))
        fritutils.termout.printSuccess("            GUID Type: {}".format(guidType))
        fritutils.termout.printSuccess("            Type name: {}".format(partTypeName))
        fritutils.termout.printSuccess("            Partition GUID: {}".format(guidPart))
        fritutils.termout.printSuccess("            Partition name: {}".format(partName))
        fritutils.termout.printSuccess("            LBA start: {} -- End: {}".format(lbaStart, lbaEnd))
        fritutils.termout.printSuccess("            Size: {}".format(fritutils.humanize(partSize)))
        fs = detectFs(fname, lbaStart * 512)
        if fs:
            FileSystems.append(fs)
    return FileSystems


def getFileSystems(fname):
    FileSystems = []
    buf = getBuffer(fname,0,512)
    FileSystems = detectDosMap(fname,buf)
    # Now we search for GPT
    FileSystems += detectGPT(fname)
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

