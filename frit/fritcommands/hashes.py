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

def updateDb(dbFile,hmd5,hsha1,hsha256,hssdeep):
    fname = os.path.join(dbFile.fullpath.fullpath,dbFile.filename)
    if not dbFile.md5:
        nMd5 = fritModel.Md5.query.filter_by(md5=hmd5).first()
        if not nMd5:
            nMd5 = fritModel.Md5()
            nMd5.md5 = hmd5
        nMd5.files.append(dbFile)
        fritModel.elixir.session.commit()
    else:
        fritutils.termout.printWarning('Md5 for "%s" is already in database.' % fname)
    if not dbFile.sha1:
        nSha1 = fritModel.Sha1.query.filter_by(sha1=hsha1).first()
        if not nSha1:
            nSha1 = fritModel.Sha1()
            nSha1.sha1 = hsha1
        nSha1.files.append(dbFile)
        fritModel.elixir.session.commit()
    else:
        fritutils.termout.printWarning('Sha1 for "%s" is already in database.' % fname)
    if not dbFile.sha256:
        nSha256 = fritModel.Sha256.query.filter_by(sha256=hsha256).first()
        if not nSha256:
            nSha256 = fritModel.Sha256()
            nSha256.sha256 = hsha256
        nSha256.files.append(dbFile)
        fritModel.elixir.session.commit()
    else:
        fritutils.termout.printWarning('Sha256 for "%s" is already in database.' % fname)
    if not dbFile.ssdeep:
        nSsdeep = fritModel.Ssdeep.query.filter_by(ssdeep=hssdeep).first()
        if not nSsdeep:
            nSsdeep = fritModel.Ssdeep()
            nSsdeep.ssdeep = hssdeep
        nSsdeep.files.append(dbFile)
        fritModel.elixir.session.commit()
    else:
        fritutils.termout.printWarning('Ssdeep for "%s" is already in database.' % fname)

def hashFile(EviDb,FsDb,realFile,dbFile):
    dname = fritutils.unicodify(os.path.dirname(dbFile))
    bname = fritutils.unicodify(os.path.basename(dbFile))
    Fpath = fritModel.FullPath.query.filter_by(fullpath=dname).first()
    nFile = fritModel.File.query.filter_by(evidence=EviDb,filesystem=FsDb,filename=bname,fullpath=Fpath).first()
    if not nFile:
        fritutils.termout.printWarning('This file cannot be found in database: %s' % (dname + '/' + bname))
    else:
        # Now we do a little check to see if an md5 exists for the file
        # if yes, we assume that all hashes are already in databases
        # we do that to avoid to do the time consuming real hashes 
        # on files. We double check the database inside updateDb()
        if not nFile.md5:
            hashes = fritutils.frithashes.hashes(realFile)
            updateDb(nFile,hashes[0],hashes[1],hashes[2],hashes[3])
        else:
            fritutils.termout.printWarning('Hashes for "%s" seems to be already in database.' % nFile.filename)
        
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
                dbfile = f[spos:]
                hashFile(EviDb,FsDb,f,dbfile)
            fs.umount('hashes')
            
            fritutils.termout.printNormal('Start inserting Hashes in database for undeleted files on "%s"\n' % fs.configName)
            for f in fs.listUndeleted():
                hashFile(EviDb,FsDb,f,f)

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

def sha1search(sha1list):
    for x in sha1list:
        if len(x) < 3:
            fritutils.termout.printWarning('"%s" is too short to be searched for.' % x)
        else:
            Sha1s = fritModel.Sha1.query.filter(fritModel.Sha1.sha1.like(unicode(x + '%'))).first()
            if Sha1s:
                for f in Sha1s.files:
                    fritutils.termout.printNormal("%s %s %s %s" % ( f.sha1.sha1, f.evidence.configName, f.filesystem.configName,f.filename))
            else:
                fritutils.termout.printNormal("%s NOT FOUND" % x)

def sha256search(sha256list):
    for x in sha256list:
        if len(x) < 3:
            fritutils.termout.printWarning('"%s" is too short to be searched for.' % x)
        else:
            Sha256s = fritModel.Sha256.query.filter(fritModel.Sha256.sha256.like(unicode(x + '%'))).first()
            if Sha256s:
                for f in Sha256s.files:
                    fritutils.termout.printNormal("%s %s %s %s" % ( f.sha256.sha256, f.evidence.configName, f.filesystem.configName,f.filename))
            else:
                fritutils.termout.printNormal("%s NOT FOUND" % x)

def csvdump(Evidences):
    for evi in Evidences:
        for fs in evi.fileSystems:
            fso =  fs.getFsDb()          
            fq = fritModel.File.query.filter(fritModel.File.filesystem==fso)
            for f in fq:
                if f.md5:
                    fritutils.termout.printNormal("%s,%s,%s,%s,%s,%s,%s,%s" % \
                    (f.evidence.configName, f.filesystem.configName,\
                     f.filename, f.md5.md5, f.sha1.sha1, f.sha256.sha256,\
                     f.ssdeep.ssdeep, f.state.state))

def factory(Evidences,args):
    """
    args are the hashes command arguments
    """
    validArgs = ('update','md5search','sha1search','sha256search', 'csvdump')
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
        if args[0] == 'sha1search':
            args.remove('sha1search')
            if len(args) < 1:
                fritutils.termout.printWarning('sha1search command need at least one sha1 to search for.')
                sys.exit(1)
            else:
                sha1search(args)
        if args[0] == 'sha256search':
            args.remove('sha256search')
            if len(args) < 1:
                fritutils.termout.printWarning('sha256search command need at least one sha256 to search for.')
                sys.exit(1)
            else:
                sha256search(args)
        if args[0] == 'csvdump':
            csvdump(Evidences)
