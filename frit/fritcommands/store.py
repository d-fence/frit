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

def store(Evidences, args):
    """
    args are the store command arguments
    """
    validArgs = ('create','dump')
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
                for evi in Evidences:
                    if evi.isLocked("store"):
                        fritutils.termout.printWarning('%s is already locked by a "store" instance.' % evi.configName)
                    else:
                        evi.mount("store","Mounted to create initial database")
                        for fs in evi.fileSystems:
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
                                    nbFiles += 1
                                    dname = fritutils.unicodify(os.path.dirname(rfile))
                                    bname = fritutils.unicodify(os.path.basename(rfile))
                                    nFile = fritModel.File()
                                    nFile.filename = bname
                                    nFile.filesize = fsize
                                    Ext = fritModel.Extension.query.filter_by(extension=ext).first()
                                    if not Ext:
                                        Ext = fritModel.Extension(extension=ext)
                                    nFile.extension = Ext
                                    Fpath = fritModel.FullPath.query.filter_by(fullpath=dname).first()
                                    if not Fpath:
                                        Fpath = fritModel.FullPath(fullpath=dname)
                                    nFile.fullpath = Fpath
                                    fritModel.elixir.session.commit()
                                    print "%d\r" % nbFiles,           
                                print "\n"
                                fs.umount("store")
                        evi.umount("store")
