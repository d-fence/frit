#!/usr/bin/python
"""
hashes command.
Computes files hashes (md5, sha1 ans ssdeep).
"""

import os
import sys
import fritutils.termout
import fritutils.fritobjects
import fritutils.fritdb as fritModel
import fritutils.frithashes

def update(Evidences):
    # First we check if the database exists
    if not os.path.exists(fritModel.DBFILE):
        fritutils.termout.printWarning('Datase does not exists yet. You should create it first with the store command.')
        sys.exit(1)
    for evi in Evidences:
        EviDb = fritModel.Evidence.query.filter_by(name=fritutils.unicodify(evi.fileName)).first()
        if not EviDb:
            fritutils.termout.printWarning('Cannot find this Evidence (%s) in database' % evi.fileName)
            break
        for fs in evi.fileSystems:
            FsDb = fritModel.Filesystem.query.filter_by(evidence=EviDb,configName=fritutils.unicodify(fs.configName)).first()
            if not FsDb:
                fritutils.termout.printWarning('Cannot find this File System (%s - %s) in database' % (evi.fileName,fs.configName))
                break
            if fs.isLocked("store") or fs.isLocked("hashes"):
                fritutils.termout.printWarning('Filesystem "%s" is already locked by a "store" or a "hashes" instance.' % fs.configName)
                break
            fs.mount('hashes', 'Hashing files')
            fritutils.termout.printNormal('Start inserting Hashes in database for regular files on "%s"\n' % fs.configName)
            spos = len(fs.fsMountPoint)
            for f in fs.listFiles():
                rfile = f[spos:]
                hashes = fritutils.frithashes.hashes(f)
                dname = fritutils.unicodify(os.path.dirname(rfile))
                bname = fritutils.unicodify(os.path.basename(rfile))
                Fpath = fritModel.FullPath.query.filter_by(fullpath=dname).first()
                nFile = fritModel.File.query.filter_by(evidence=EviDb,filesystem=FsDb,filename=bname,fullpath=Fpath).first()
                if not nFile:
                    fritutils.termout.printWarning('This file cannot be found in database: %s' % (dname + '/' + bname))
                else:
                    if not nFile.md5:
                        nMd5 = fritModel.Md5.query.filter_by(md5=hashes[0]).first()
                        if not nMd5:
                            nMd5 = fritModel.Md5()
                            nMd5.md5 = hashes[0]
                        nMd5.files.append(nFile)
                        fritModel.elixir.session.commit()
                    else:
                        fritutils.termout.printWarning('Md5 for "%s" is already in database.' % (dname + '/' + bname))
                    if not nFile.sha1:
                        nSha1 = fritModel.Sha1.query.filter_by(sha1=hashes[1]).first()
                        if not nSha1:
                            nSha1 = fritModel.Sha1()
                            nSha1.sha1 = hashes[1]
                        nSha1.files.append(nFile)
                        fritModel.elixir.session.commit()
                    else:
                        fritutils.termout.printWarning('Sha1 for "%s" is already in database.' % (dname + '/' + bname))
                    if not nFile.sha256:
                        nSha256 = fritModel.Sha256.query.filter_by(sha256=hashes[2]).first()
                        if not nSha256:
                            nSha256 = fritModel.Sha256()
                            nSha256.sha256 = hashes[2]
                        nSha256.files.append(nFile)
                        fritModel.elixir.session.commit()
                    else:
                        fritutils.termout.printWarning('Sha256 for "%s" is already in database.' % (dname + '/' + bname))
                    if not nFile.ssdeep:
                        nSsdeep = fritModel.Ssdeep.query.filter_by(ssdeep=hashes[3]).first()
                        if not nSsdeep:
                            nSsdeep = fritModel.Ssdeep()
                            nSsdeep.ssdeep = hashes[3]
                        nSsdeep.files.append(nFile)
                        fritModel.elixir.session.commit()
                    else:
                        fritutils.termout.printWarning('Ssdeep for "%s" is already in database.' % (dname + '/' + bname))
            fs.umount('hashes')

def md5search(md5list):
    for x in md5list:
        if len(x) < 3:
            fritutils.termout.printWarning('"%s" is too short to be searched for.' % x)
        else:
            Md5s = fritModel.Md5.query.filter(fritModel.Md5.md5.like(unicode(x + '%'))).first()
            if Md5s:
                for f in Md5s.files:
                    fritutils.termout.printNormal("%s %s %s %s" % ( f.md5.md5, f.evidence.configName, f.filesystem.configName,f.filename))
            else:
                fritutils.termout.printNormal("%s NOT FOUND" % x)

def factory(Evidences,args):
    """
    args are the hashes command arguments
    """
    validArgs = ('update','md5search','sha1search')
    if not args or len(args) == 0:
        fritutils.termout.printWarning('hashes command need at least an argument')
        sys.exit(1)
    elif args[0] not in validArgs:
        fritutils.termout.printWarning('hashes command need a valid argument (%s)' % ', '.join(validArgs))
        sys.exit(1)
    else:
        if args[0] == 'update':
            update(Evidences)
        if args[0] == 'md5search':
            args.remove('md5search')
            if len(args) < 1:
                fritutils.termout.printWarning('md5search command need at least one md5 to search for.')
                sys.exit(1)
            else:
                md5search(args)
