#!/usr/bin/python
"""
module for the sqlite support
"""

import elixir
from sqlalchemy import select, func
import os.path

DBFILE = ".frit/frit.sqlite"

elixir.metadata.bind = "sqlite:///" + DBFILE
elixir.metadata.bind.echo = False

class File(elixir.Entity):
    filename = elixir.Field(elixir.Unicode(300))
    filesize = elixir.Field(elixir.Integer)
    fullpath = elixir.ManyToOne('FullPath')
    extension = elixir.ManyToOne('Extension')
    mimetype = elixir.ManyToOne('MimeType')
    md5 = elixir.ManyToOne('Md5')
    sha1 = elixir.ManyToOne('Sha1')
    ssdeep = elixir.ManyToOne('Ssdeep')

class Extension(elixir.Entity):
    extension = elixir.Field(elixir.Unicode(50))
    files = elixir.OneToMany('File')

class FullPath(elixir.Entity):
    fullpath = elixir.Field(elixir.Unicode(900))
    files = elixir.OneToMany('File')
    
class MimeType(elixir.Entity):
    mimetype = elixir.Field(elixir.Unicode(150))
    files = elixir.OneToMany('File')

class Md5(elixir.Entity):
    md5 = elixir.Field(elixir.Unicode(32))
    files = elixir.OneToMany('File')

class Sha1(elixir.Entity):
    sha1 = elixir.Field(elixir.Unicode(40))
    files = elixir.OneToMany('File')

class Ssdeep(elixir.Entity):
    ssdeep = elixir.Field(elixir.Unicode(150))
    files = elixir.OneToMany('File')

elixir.setup_all()
    
def createDb():
    if not os.path.exists(DBFILE):
        elixir.create_all()
