#!/usr/bin/python
"""
extensions command.
Used to manipulate file based on their extensions.
"""
import sys
import os.path
import shutil
import fritutils
import fritutils.termout
import fritutils.fritdb as fritModel
from sqlalchemy import func

def extractFile(toExtract,destination):
    if not os.path.exists(destination):
        os.makedirs(destination)
    if not os.path.exists(destination+toExtract):
        shutil.copy2(toExtract,destination)


def factory(Evidences, args):
    validArgs = ('list', 'extract')
    if not args or len(args) == 0:
        fritutils.termout.printWarning('extensions command need at least an argument')
        sys.exit(1)
    elif args[0] not in validArgs:
        fritutils.termout.printWarning('extensions command need a valid argument (%s)' % ', '.join(validArgs))
        sys.exit(1)
    else:
        if args[0] == 'list':
            # the remaining args should be the extensions that we want to list
            # if there is no more args, we list all extensions
            args.remove('list')
            if not args or len(args) == 0:
                extList = []
                for ex in fritModel.elixir.session.query(fritModel.Extension.extension).all():
                    extList.append(ex[0])
            else:
                extList = []
                for ex in args:
                    extList.append(fritutils.unicodify(ex))
            for evi in Evidences:
                fritutils.termout.printMessage(evi.configName)
                for fs in evi.fileSystems:
                    fritutils.termout.printMessage("\t%s" % fs.configName)
                    for ext in sorted(extList):
                        e = fritModel.Extension.query.filter_by(extension=ext).first()
                        fso =  fritModel.Filesystem.query.filter_by(configName=fritutils.unicodify(fs.configName)).first()
                        fstate = fritModel.FileState.query.filter_by(state=u'Normal').first()
                        if e and fso :
                            fq = fritModel.File.query.filter_by(extension=e,filesystem=fso,state=fstate)
                            sizeSum = 0
                            sizeSum = fq.value(func.sum(fritModel.File.filesize))
                            fritutils.termout.printSuccess("\t\t%s : %d (%s)" % (ext, fq.count(), fritutils.humanize(sizeSum)))
                        else:
                            fritutils.termout.printSuccess("\t\t%s : 0 (0)" % (ext))
        elif args[0] == 'extract':
            args.remove('extract')
            if not args or len(args) == 0:
                extList = []
                for ex in fritModel.elixir.session.query(fritModel.Extension.extension).all():
                    extList.append(ex[0])
            else:
                extList = []
                for ex in args:
                    extList.append(fritutils.unicodify(ex))
            for evi in Evidences:
                fritutils.termout.printMessage(evi.configName)
                evi.mount('extensions', 'Extracting files based on extensions')
                for fs in evi.fileSystems:
                    fritutils.termout.printMessage("\t%s" % fs.configName)
                    fs.mount('extensions', 'Extracting files based on extensions')
                    for ext in sorted(extList):
                        e = fritModel.Extension.query.filter_by(extension=ext).first()
                        fso =  fritModel.Filesystem.query.filter_by(configName=fritutils.unicodify(fs.configName)).first()
                        fstate = fritModel.FileState.query.filter_by(state=u'Normal').first()
                        if e and fso :
                            fq = fritModel.File.query.filter_by(extension=e,filesystem=fso,state=fstate)
                            sizeSum = 0
                            sizeSum = fq.value(func.sum(fritModel.File.filesize))
                            fritutils.termout.printMessage("Extracting %d files (%s)" % (fq.count(),fritutils.humanize(sizeSum)))
                            for fileObject in fq:
                                toExtract = os.path.join('.frit/filesystems/',evi.configName,fs.configName,fileObject.fullpath.fullpath[1:],fileObject.filename)
                                Destination = os.path.join('.frit/extractions/by_extensions/',evi.configName,fs.configName,ext[1:],fileObject.fullpath.fullpath[1:])
                                extractFile(toExtract,Destination)
                        else:
                            fritutils.termout.printWarning('No "%s" to extract' % (ext))
                    fs.umount('extensions')
                evi.umount('extensions')
