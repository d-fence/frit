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
import fritutils.fritlog

logger = fritutils.fritlog.loggers['storeLog']

def insertFile(File,prefix,state,eviDb,fsDb):
    """
    A function that insert a file into the database.
    prefix: the prefix to remove from the path before inserting (.frit/filesystems/Evidencex/filesystemx...)
    state: the database file state (normal, undeleted, carved, contained ...)
    """
    fsize = 0
    try:
        fsize = os.path.getsize(File)
    except:
        print >> sys.stderr, "ERROR GETTING SIZE OF: %s\n" % File

    fname,ext = os.path.splitext(File)
    ext = fritutils.unicodify(ext.lower())
    if ext == '':
        ext = u'No Extension'

    dname = fritutils.unicodify(os.path.dirname(File))
    if prefix != '':
        dname = dname.replace(prefix,'')
        if dname == '':
            dname = u'/'
        
    bname = fritutils.unicodify(os.path.basename(File))
    
    Ext = fritModel.Extension.query.filter_by(extension=ext).first()
    if not Ext:
        Ext = fritModel.Extension(extension=ext)
    Fpath = fritModel.FullPath.query.filter_by(fullpath=dname).first()
    if not Fpath:
        Fpath = fritModel.FullPath(fullpath=dname)
    
    nFile = fritModel.File.query.filter_by(evidence=eviDb,filesystem=fsDb,filename=bname,fullpath=Fpath).first()
    if not nFile:
        nFile = fritModel.File(evidence=eviDb,filesystem=fsDb)
    nFile.state = fritModel.FileState.query.filter_by(state=state).first()
    nFile.filename = bname
    nFile.filesize = fsize
    nFile.fullpath = Fpath
    nFile.extension = Ext
                           
    fritModel.elixir.session.commit()
    
                            
def update(Evidences):
    for evi in Evidences:
        # evidence creation in the database
        EviDb = fritModel.Evidence.query.filter_by(name=fritutils.unicodify(evi.fileName)).first()
        if not EviDb:
            EviDb = fritModel.Evidence(name=fritutils.unicodify(evi.fileName),configName=fritutils.unicodify(evi.configName))
        if evi.isLocked("store"):
            fritutils.termout.printWarning('%s is already locked by a "store" instance.' % evi.configName)
        else:
            # we start to insert filesystems normal files metadata in the database
            evi.mount("store","Mounted to create initial database")
            for fs in evi.fileSystems:
                # first, we count the files that are already in the DB
                fcount = fs.dbCountFiles()[u'Normal']
                if fcount['Files'] > 0:
                    fritutils.termout.printMessage('%d files are already in the database, not inserting.' % fcount['Files'])
                else:
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
                            insertFile(f,fs.fsMountPoint,u'Normal',EviDb,FsDb)
                            nbFiles += 1
                            print "\t%s : %d\r" % (fs.configName,nbFiles),           
                    print "\n"
                    fs.umount("store")
            evi.umount("store")

def storeUndeleted(Evidences):
    """
    A function to store the metadata of undeleted files.
    Here we don't need to mount anything.
    """
    for evi in Evidences:
        # evidence creation in the database
        EviDb = fritModel.Evidence.query.filter_by(name=fritutils.unicodify(evi.fileName)).first()
        if not EviDb:
            EviDb = fritModel.Evidence(name=fritutils.unicodify(evi.fileName),configName=fritutils.unicodify(evi.configName))
        for fs in evi.fileSystems:
            # filesystem creation in the database
            FsDb = fritModel.Filesystem.query.filter_by(evidence=EviDb,configName=fritutils.unicodify(fs.configName)).first()
            if not FsDb:
                FsDb = fritModel.Filesystem(evidence=EviDb,configName=fritutils.unicodify(fs.configName))

            nbFiles = 0
            fritutils.termout.printNormal('Start inserting undeleted files metadata in database for "%s"\n' % fs.configName)
            for f in fs.listUndeleted():
                insertFile(f,'',u'Undeleted',EviDb,FsDb)                                    
                nbFiles += 1
                print "\t%s : %d\r" % (fs.configName,nbFiles),           
        print "\n"

def storeEmails(Evidences):
    """
    A function to store the metadata of extracted emails files.
    """
    for evi in Evidences:
        # evidence creation in the database
        EviDb = fritModel.Evidence.query.filter_by(name=fritutils.unicodify(evi.fileName)).first()
        if not EviDb:
            EviDb = fritModel.Evidence(name=fritutils.unicodify(evi.fileName),configName=fritutils.unicodify(evi.configName))
        for fs in evi.fileSystems:
            # filesystem creation in the database
            FsDb = fritModel.Filesystem.query.filter_by(evidence=EviDb,configName=fritutils.unicodify(fs.configName)).first()
            if not FsDb:
                FsDb = fritModel.Filesystem(evidence=EviDb,configName=fritutils.unicodify(fs.configName))

            nbFiles = 0
            fritutils.termout.printNormal('Start inserting emails files metadata in database for "%s"\n' % fs.configName)
            for f in fs.listEmails():
                insertFile(f,'',u'Contained',EviDb,FsDb)                                    
                nbFiles += 1
                print "\t%s : %d\r" % (fs.configName,nbFiles),           
        print "\n"
    
def storeClear(Evidences):
    """
    A function to delete records for specified Evidences
    """
    for evi in Evidences:
        eviNb = 0
        for fs in evi.fileSystems:
            fso =  fs.getFsDb()          
            fq = fritModel.File.query.filter(fritModel.File.filesystem==fso)
            nb = fq.count()
            fritutils.termout.printNormal('Deleting %d records for %s / %s' % (nb,evi.configName,fs.configName))
            fq.delete()
            fritModel.elixir.session.commit()
            fp = fritModel.FullPath.query.join(fritModel.File.filesystem).filter(fritModel.File.filesystem==fso)

def filenameSearch(Evidences,args):
    """
    A function to search for a file based on filename(s).
    Filenames to search are the args
    """
    for evi in Evidences:
        for searchTerm in args:
            searchTerm = searchTerm.decode('utf-8')
            fritutils.termout.printNormal("Searching for %s in %s" % (searchTerm, evi.configName))
            for f in fritModel.fileNameSearch(evi,searchTerm):
                fritutils.termout.printMessage("\t%s" % f.fullFileSpec())

def store(Evidences, args, options):
    """
    args are the store command arguments
    """
    logger.info('Starting store command.')
    validArgs = ('create', 'update', 'dump', 'undeleted', 'clear', 'search', 'emails')
    if not args or len(args) == 0:
        fritutils.termout.printWarning('store command need at least an argument')
        logger.warning('No argument given to the command.')
        sys.exit(1)
    elif args[0] not in validArgs:
        fritutils.termout.printWarning('store command need a valid argument (%s)' % ', '.join(validArgs))
        logger.warning('invalid argument %s' % args[0])
        sys.exit(1)
    else:
        if args[0] == 'create':
            logger.info('Starting create subcommand.')
            if os.path.exists(fritutils.fritdb.DBFILE):
                fritutils.termout.printWarning('Database already exists, cannot create it.')
            else:
                fritModel.createDb()
                update(Evidences)
        else:
            if not os.path.exists(fritutils.fritdb.DBFILE):
                fritutils.termout.printWarning('Database does not exists, use the "store create" command first.')
                logger.warning('Database does not exists.')
            else:
                if args[0] == 'update':
                    logger.info('Starting update subcommand.')
                    update(Evidences)
                if args[0] == 'undeleted':
                    logger.info('Starting undeleted subcommand.')
                    storeUndeleted(Evidences)
                if args[0] == 'clear':
                    logger.info('Starting clear subcommand.')
                    storeClear(Evidences)
                if args[0] == 'search':
                    logger.info('Starting search subcommand.')
                    args.remove("search")
                    filenameSearch(Evidences, args)
                if args[0] == 'emails':
                    logger.info('Starting emails subcommand.')
                    storeEmails(Evidences)
