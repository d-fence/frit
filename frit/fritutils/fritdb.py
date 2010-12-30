#!/usr/bin/python
"""
module for the sqlite support
FILESTATES:
Normal: normal files.
Undeleted: undeleted fiels.
Carved: carved files.
Contained: Files that were contained inside a parent file (a zip, a mailbox, a rar, ...)
"""

import elixir
from sqlalchemy import select, func
import os.path
import fritutils

DBFILE = ".frit/frit.sqlite"
FILESTATES = (u'Normal', u'Undeleted', u'Carved', u'Contained')

elixir.metadata.bind = "sqlite:///" + DBFILE
elixir.metadata.bind.echo = False

class Evidence(elixir.Entity):
    name = elixir.Field(elixir.Unicode(300))
    configName = elixir.Field(elixir.Unicode(300))

class Filesystem(elixir.Entity):
    evidence = elixir.ManyToOne('Evidence')
    configName = elixir.Field(elixir.Unicode(300))

class FileState(elixir.Entity):
    state = elixir.Field(elixir.Unicode(20))

class File(elixir.Entity):
    #parent = elixir.ManyToOne('File')
    #children = elixir.OneToMany('File')
    evidence = elixir.ManyToOne('Evidence')
    filesystem = elixir.ManyToOne('Filesystem')
    state = elixir.ManyToOne('FileState')
    filename = elixir.Field(elixir.Unicode(300), index=True)
    filesize = elixir.Field(elixir.Integer)
    fullpath = elixir.ManyToOne('FullPath')
    extension = elixir.ManyToOne('Extension')
    mimetype = elixir.ManyToOne('MimeType')
    md5 = elixir.ManyToOne('Md5')
    sha1 = elixir.ManyToOne('Sha1')
    sha256 = elixir.ManyToOne('Sha256')
    ssdeep = elixir.ManyToOne('Ssdeep')
    
class Extension(elixir.Entity):
    extension = elixir.Field(elixir.Unicode(50), index=True)
    files = elixir.OneToMany('File')

class FullPath(elixir.Entity):
    fullpath = elixir.Field(elixir.Unicode(900), index=True)
    files = elixir.OneToMany('File')
    
class MimeType(elixir.Entity):
    mimetype = elixir.Field(elixir.Unicode(150))
    files = elixir.OneToMany('File')

class Md5(elixir.Entity):
    md5 = elixir.Field(elixir.Unicode(32), index=True)
    files = elixir.OneToMany('File')

class Sha1(elixir.Entity):
    sha1 = elixir.Field(elixir.Unicode(40), index=True)
    files = elixir.OneToMany('File')

class Sha256(elixir.Entity):
    sha256 = elixir.Field(elixir.Unicode(64), index=True)
    files = elixir.OneToMany('File')

class Ssdeep(elixir.Entity):
    ssdeep = elixir.Field(elixir.Unicode(150), index=True)
    files = elixir.OneToMany('File')

elixir.setup_all()

def dbExists():
    """
    A function that return True if the db exists
    """
    if not os.path.exists(DBFILE):
        return False
    else:
        return True
   
def createDb():
    """
    A function to create the database and fill some tables
    """
    if not dbExists():
        elixir.create_all()
        for fstate in FILESTATES:
            fis = FileState(state=fstate)
            elixir.session.commit()
            
def listExtensions(Evidences,extlist,states):
        """
        A function to print a count and a size sum of the specified extension
        for all filsystems of specified Evidences list.
        """
        totalExt = {}
        for ext in extlist:
            totalExt[ext] = [0,0]
        grandTotalNb = 0
        grandTotalSize = 0
        for evi in Evidences:
            fritutils.termout.printNormal('%s (%s)' % (evi.configName,evi.fileName))
            for filesystem in evi.fileSystems:
                fritutils.termout.printNormal('\t%s' % filesystem.configName)
                totalSize = 0
                totalNumber = 0
                fso =  filesystem.getFsDb()
                for ext in extlist:
                    for state in states:
                        fq = File.query.filter(File.filesystem==fso)
                        fq = fq.filter(File.state.has(state=state))
                        fq = fq.filter(File.extension.has(extension=ext))
                        nb = fq.count()
                        if nb >0 :
                            size=fq.value(func.sum(File.filesize))
                            fritutils.termout.printNormal('\t\t%s %d (%s) (state: %s)' % (ext,nb,fritutils.humanize(size),state))
                            totalSize += size
                            totalNumber += nb
                            grandTotalNb += nb
                            grandTotalSize += size
                            if ext in totalExt.keys():
                                totalExt[ext][0] += nb
                                totalExt[ext][1] += size
                            else:
                                totalExt[ext] = [nb, size]
                fritutils.termout.printNormal('\t\tFilesystem Total Files : %d' % totalNumber)
                fritutils.termout.printNormal('\t\tFilesystem Total Size : %s' % fritutils.humanize(totalSize))
        fritutils.termout.printSuccess('Summary:')
        for ext in extlist:
            fritutils.termout.printNormal('\t%s %d %s' % (ext, totalExt[ext][0], fritutils.humanize(totalExt[ext][1])))
        fritutils.termout.printNormal('Total files (size): %d (%s)' % (grandTotalNb, fritutils.humanize(grandTotalSize)))
        
def fileNameSearch(Evidence,fileName):
    """
    A function that yield files where the filename match.
    """
    for filesystem in Evidence.fileSystems:
        fso = filesystem.getFsDb()
        fq = File.query.filter(File.filesystem==fso)
        fq = fq.filter(File.filename.like(unicode(fileName)))
        for f in fq.all():
            yield(f)
