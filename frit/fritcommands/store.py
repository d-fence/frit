#!/usr/bin/python
"""
store command.
Used to store various data in a sqlite database.
"""
import sys
import os.path
import fritutils
import fritutils.termout
import fritutils.fritdb as fritModel

def update(Evidences):
    for evi in Evidences:
        # evidence creation in the database
        EviDb = fritModel.Evidence.query.filter_by(name=fritutils.unicodify(evi.fileName)).first()
        if not EviDb:
            EviDb = fritModel.Evidence(name=fritutils.unicodify(evi.fileName),configName=fritutils.unicodify(evi.configName))
        if evi.isLocked("store"):
            fritutils.termout.printWarning('%s is already locked by a "store" instance.' % evi.configName)
        else:
            evi.mount("store","Mounted to create initial database")
            for fs in evi.fileSystems:
                # filesystem creation in the database
                FsDb = fritModel.Filesystem.query.filter_by(evidence=EviDb,configName=fritutils.unicodify(fs.configName)).first()
                if not FsDb:
                    FsDb = fritModel.Filesystem(evidence=EviDb,configName=fritutils.unicodify(fs.configName))
                if fs.isLocked("store"):
                    fritutils.termout.printWarning('Filesystem "%s" is already locked by a "store" instance.' % fs.configName)
                else:
                    fs.mount("store","Mounted to create initial database")
                    spos = len(fs.fsMountPoint)
                    nbFiles = 0
                    fritutils.termout.printNormal('Start inserting files metadata in database for "%s"\n' % fs.configName)
                    for f in fs.listFiles():                                    
                        rfile = f[spos:]
                        fsize = 0
                        try:
                            fsize = os.path.getsize(f)
                        except:
                            print >> sys.stderr, "ERROR GETTING SIZE OF: %s\n" % f
                        fname,ext = os.path.splitext(rfile)
                        ext = fritutils.unicodify(ext.lower())
                        if ext == '':
                            ext = u'No Extension'
                        nbFiles += 1
                        dname = fritutils.unicodify(os.path.dirname(rfile))
                        bname = fritutils.unicodify(os.path.basename(rfile))
                        Ext = fritModel.Extension.query.filter_by(extension=ext).first()
                        if not Ext:
                            Ext = fritModel.Extension(extension=ext)
                        Fpath = fritModel.FullPath.query.filter_by(fullpath=dname).first()
                        if not Fpath:
                            Fpath = fritModel.FullPath(fullpath=dname)
                        
                        nFile = fritModel.File.query.filter_by(evidence=EviDb,filesystem=FsDb,filename=bname,fullpath=Fpath).first()
                        if not nFile:
                            nFile = fritModel.File(evidence=EviDb,filesystem=FsDb)
                        nFile.state = fritModel.FileState.query.filter_by(state=u'Normal').first()
                        nFile.filename = bname
                        nFile.filesize = fsize
                        nFile.fullpath = Fpath
                        nFile.extension = Ext
                                               
                        fritModel.elixir.session.commit()
                        print "\t%s : %d\r" % (fs.configName,nbFiles),           
                    print "\n"
                    fs.umount("store")
            evi.umount("store")

def store(Evidences, args):
    """
    args are the store command arguments
    """
    validArgs = ('create', 'update', 'dump')
    if not args or len(args) == 0:
        fritutils.termout.printWarning('store command need at least an argument')
        sys.exit(1)
    elif args[0] not in validArgs:
        fritutils.termout.printWarning('store command need a valid argument (%s)' % ', '.join(validArgs))
        sys.exit(1)
    else:
        if args[0] == 'create':
            if os.path.exists(fritutils.fritdb.DBFILE):
                fritutils.termout.printWarning('Database already exists, cannot create it.')
            else:
                fritModel.createDb()
                update(Evidences)
        if args[0] == 'update':
            if not os.path.exists(fritutils.fritdb.DBFILE):
                fritutils.termout.printWarning('Database does not exists, use the "store create" command first.')
            else:
                update(Evidences)            
                

