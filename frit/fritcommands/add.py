#!/usr/bin/python
"""
add command.
This command is used to add a file in a config file.
Frit then tries to recognize the container file and the contained file systems.
"""

import os
import fritutils

def factory(args):
    """
    The factory receive the remaining args.
    Those args are files that the user wants to add in the config file.
    We should first do some sanity checks to be sure that those files are
    readable ...
    """

    fritConfig = fritutils.getConfig()

    validContainersFormat = ('dd', 'aff', 'ewf','rofs')
    cfiles = fritutils.fritconf.configContainersFiles(fritConfig)
    for fileName in args.files:
        argPath = fileName
        fileName = os.path.abspath(fileName)
        if not os.path.exists(fileName):
            fritutils.termout.printWarning("File %s does't exist." % fileName)
        elif os.getcwd() not in fileName:
             fritutils.termout.printWarning("File %s is outside of the base directory." % fileName)
        elif fileName in cfiles:
            fritutils.termout.printWarning("File %s already in config file." % fileName)
        else:
            evi = None
            cformat = fritutils.containerprobe.detectContainer(fileName)
            if cformat in validContainersFormat:
                fritutils.termout.printSuccess('Found that %s is a "%s" container.' % (argPath, cformat))
                # creating an Evidence object
                if cformat == 'dd':
                    evi = fritutils.fritobjects.DdEvidence(filename=argPath,configName='tempconfig')
                elif cformat == 'aff':
                    evi = fritutils.fritobjects.AffEvidence(filename=argPath,configName='tempconfig')
                elif cformat == 'ewf':
                    # aff does not support ewf anymore.
                    evi = fritutils.fritobjects.EwfEvidence(filename=argPath,configName='tempconfig')
                elif cformat == 'rofs':
                    evi = fritutils.fritobjects.RofsEvidence(filename=argPath,configName='tempconfig')

                # Now we, if we have an evidence, we mount it and probe it for the contained filesystems
                if evi:
                    # rofs special case (no need to mount anything)
                    if evi.getFormat() == 'rofs':
                        newFs = fritutils.fritobjects.RoDirFileSystem(0,'tempconfig',evi)
                        evi.fileSystems.append(newFs)
                    else:
                        try:
                            evi.mount('add','probing for filesystems')
                        except:
                            fritutils.termout.printWarning('Unable to mount %s' % evi.configName)
                        if evi.isMounted():
                            evi.populateRawImage()
                            fsys = fritutils.fsprobe.getFileSystems(evi.rawImage)
                            for fs in fsys:
                                newFs = None
                                if fs.name == 'NTFS':
                                    newFs = fritutils.fritobjects.NtfsFileSystem(fs.position,'tempconfig',evi)
                                elif fs.name == 'FAT':
                                    newFs = fritutils.fritobjects.FatFileSystem(fs.position,'tempconfig',evi)
                                elif fs.name == 'ISO9660':
                                    newFs = fritutils.fritobjects.ISO9660FileSystem(fs.position,'tempconfig',evi)
                                if newFs:
                                    fritutils.termout.printSuccess('\tFound "%s" filesystem at offset %d' % (fs.name, fs.position))
                                    evi.fileSystems.append(newFs)
                        evi.umount('add')
                    # and now we write the config file
                    fritutils.fritconf.addEvidence(fritConfig,evi)
