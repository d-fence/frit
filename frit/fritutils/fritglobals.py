#!/usr/bin/python
# Module to defines global variables
# These variables maybe configured from /etc/frit/fritconfig
# or ~/.fritconfig/fritconfig

import os.path
import configobj
import fritutils.fritlog

confLogger = fritutils.fritlog.loggers['globalsLog']

# a special str class for the tools that can check if the tool exists
class ExternalTool(str):
    def __init__(self,toolPath):
        self.toolPath = toolPath

    def __repr__(self):
        return self.toolPath

    def __str__(self):
        return self.toolPath

    def check(self):
        return os.path.exists(self.toolPath)

globalFile = '/etc/frit/fritconfig'
if os.path.exists(globalFile):
    confLogger.info('Config file "%s" found ' % globalFile)
    globalConfig = configobj.ConfigObj('/etc/frit/fritconfig',indent_type='    ')
else:
    confLogger.warning('Config file "%s" not found' % globalFile)
    globalConfig = configobj.ConfigObj()

homeFile = os.path.join(os.path.expanduser('~'),'.fritconfig','fritconfig')

if os.path.exists(homeFile):
    confLogger.info('Home config file "%s" found' % homeFile)
    homeConfig = configobj.ConfigObj(homeFile,indent_type='    ')
else:
    confLogger.warning('Home config file "%s" not found' % homeFile)
    homeConfig = configobj.ConfigObj()


globalConfig.merge(homeConfig)

# Now getting the tools sections of the config files
# if there is no tools section, we create an empty configobj
# that way, we can giv default values

ctools = globalConfig.get('tools')
if not ctools:
    ctools = configobj.ConfigObj()

toolbox = []

AFFMOUNT = ExternalTool(ctools.get('AFFMOUNT', default='/usr/bin/affuse'))
toolbox.append(AFFMOUNT)

FUSERMOUNT = ExternalTool(ctools.get('FUSERMOUNT', default='/bin/fusermount'))
toolbox.append(FUSERMOUNT)

NTFS3G = ExternalTool(ctools.get('NTFS3G', default='/bin/ntfs-3g'))
toolbox.append(NTFS3G)

FUSEISO = ExternalTool(ctools.get('FUSEISO', default='/usr/bin/fuseiso'))
toolbox.append(FUSEISO)

SUDO = ExternalTool(ctools.get('SUDO', default='/usr/bin/sudo'))
toolbox.append(SUDO)

MOUNT = ExternalTool(ctools.get('MOUNT', default='/bin/mount'))
toolbox.append(MOUNT)

UMOUNT = ExternalTool(ctools.get('UMOUNT', default='/bin/umount'))
toolbox.append(UMOUNT)

FUSEEXT2 = ExternalTool(ctools.get('FUSEEXT2', default='/usr/bin/fuseext2'))
toolbox.append(FUSEEXT2)

FUSE2FS = ExternalTool(ctools.get('FUSE2FS', default='/usr/sbin/fuse2fs'))
toolbox.append(FUSE2FS)

ROFS = ExternalTool(ctools.get('ROFS', default='/usr/bin/rofs'))
toolbox.append(ROFS)

XMOUNT = ExternalTool(ctools.get('XMOUNT', default='/usr/bin/xmount'))
toolbox.append(XMOUNT)

DD = ExternalTool(ctools.get('DD', default='/bin/dd'))
toolbox.append(DD)

AFFCAT = ExternalTool(ctools.get('AFFCAT', default='/usr/bin/affcat'))
toolbox.append(AFFCAT)

EWFEXPORT = ExternalTool(ctools.get('EWFEXPORT', default='/usr/bin/ewfexport'))
toolbox.append(EWFEXPORT)

EWFMOUNT = ExternalTool(ctools.get('EWFMOUNT', default='/usr/bin/ewfmount'))
toolbox.append(EWFMOUNT)

PFFEXPORT  = ExternalTool(ctools.get('PFFEXPORT', default= '/usr/bin/pffexport'))
toolbox.append(PFFEXPORT)

SSDEEP = ExternalTool(ctools.get('SSDEEP', default='/usr/bin/ssdeep'))
toolbox.append(SSDEEP)

MMLS = ExternalTool(ctools.get('MMLS', default='/usr/bin/mmls'))
toolbox.append(MMLS)

NTFSUNDELETE = ExternalTool(ctools.get('NTFSUNDELETE', default='/sbin/ntfsundelete'))
toolbox.append(MMLS)

TSKRECOVER = ExternalTool(ctools.get('TSKRECOVER', default='/usr/bin/tsk_recover'))
toolbox.append(TSKRECOVER)

BLKLS = ExternalTool(ctools.get('BLKLS', default='/usr/bin/blkls'))
toolbox.append(BLKLS)

PHOTOREC = ExternalTool(ctools.get('PHOTOREC', default='/usr/bin/photorec'))
toolbox.append(PHOTOREC)

VSHADOWMOUNT = ExternalTool(ctools.get('VSHADOWMOUNT', default='/usr/bin/vshadowmount'))
toolbox.append(VSHADOWMOUNT)

# configuration of ext2/3/4 mount method
# possible values at this moment: fuse2fs or fuseext2
EXT2METHOD = globalConfig.get('EXT2METHOD', default='fuse2fs')

# Possible base directories for home directories
POSSIBLE_HOME_BASES = globalConfig.get('POSSIBLE_HOME_BASES',
    default= ('home', 'USERS', 'Users', 'users', 'Documents and Setting',))
