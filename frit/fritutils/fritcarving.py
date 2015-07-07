#!/usr/bin/python
"""
Utilities to carve for files with various external tools
"""

import subprocess
import os
import os.path
import re
import fritutils.termout
from fritutils.fritglobals import *

PhotoRecTypes = {
    'Archive' : [ '7z', 'a', 'ace', 'arj', 'bkf', 'bz2', 'cab', 'dar',
                  'deb', 'dump', 'gz', 'lzh', 'lzo', 'par2', 'rar', 'rpm',
                  'stu', 'tar', 'tar.gz', 'vbm', 'wim', 'xz', 'zip' ],
    'Picture' : [ 'albm', 'arw', 'bmp', 'cam', 'cdd', 'cdl', 'comicdoc',
                  'cr2', 'crw', 'ctg', 'cue', 'db', 'dcr', 'djv', 'dng',
                  'dp', 'dpx', 'dsc', 'dwg', 'emf', 'fh10', 'fh5', 'gif',
                  'ico', 'jng', 'jpg', 'kra', 'mng', 'mpo', 'mrw', 'nef',
                  'orf', 'pbm', 'pct', 'pcx', 'psb', 'pef', 'pgm', 'png',
                  'pnm', 'ppm', 'pproj', 'psd', 'psf', 'psp', 'pts', 'qkt',
                  'raf', 'raw', 'rdc', 'rw2', 'sr2', 'svg', 'tif', 'wdp',
                  'x3f', 'xcf', 'xv' ],
    'Video' : [ '3g2', '3gp', 'ari', 'asf', 'wma', 'wmv', 'avi', 'camrec',
                'fla', 'flv', 'm2t', 'm2ts', 'mhbd', 'mkv', 'mlv', 'mov',
                'mp4', 'mpg', 'ogv', 'pvp', 'rm', 'swc', 'swf', 'TiVo',
                'ts', 'tod', 'webm', 'wmf', 'wnk', 'wtv' ],
    'Office' : [ 'accdb', 'ai', 'csv', 'cwk', 'doc', 'docx', 'fp7', 'fp12',
                 'mdb', 'odg', 'odp', 'ods', 'odt', 'one', 'pages', 'ppt',
                 'pptx', 'pub', 'qpw', 'rtf', 'sda', 'sdc', 'sdd', 'sdw',
                 'sxc', 'sxd', 'sxi', 'sxw', 'vsd', 'wpd', 'wps', 'xlr',
                 'xls', 'xlsx', 'wdb', 'wk4', 'wks' ],
    'Various' : [ 'ab', 'bac', 'cow', 'dbx', 'dex', 'e01', 'ecr', 'eCryptfs',
                  'edb', 'elf', 'eps', 'evt', 'exe', 'gho', 'hds', 'ics',
                  'jar', 'json', 'nk2', 'nsf', 'pcap', 'pgp', 'pst', 'reg',
                  'rlv', 'sqlite', 'sql', 'sqm', 'url', 'vcf', 'wallet',
                  'vmdk', 'wab', 'wim', ]
    }


def isPhotorecFormat(f):
    """
    Check if f is a known photorec extension format
    """
    for t in PhotoRecTypes:
        if f in PhotoRecTypes[t]:
            return True
    return False

def Photorec(target,destination,args):
    """
    target: the file on which to perform photorec carving
    destination: the destination dir
    args: A list of extension to carve for or group of extensions (pictures, music ...)
    """
    fritutils.termout.printMessage('\tPerforming photorec on "%s". Results goes in "%s".' % (target,destination))
    formats = set()
    # now, we parse the args to see what kind of files we want to carve for
    for a in args:
        # First, if a is a familly, we add all types
        if a in PhotoRecTypes:
            for t in PhotoRecTypes[a]:
                formats.add(t)
        else:
            if isPhotorecFormat(a):
                formats.add(a)
    if not formats:
        optionString = 'fileopt,everything,enable'
    else:
        optionString = 'fileopt,everything,disable'
        for f in formats:
            optionString += ',' + f + ',enable'

    optionString += ',search'
    photorec = subprocess.Popen([PHOTOREC, '/d', destination, '/cmd', target, optionString ])
    photorec.wait()
    if photorec.returncode > 0:
        fritutils.termout.printWarning("Error with photorec")
    fritutils.termout.printSuccess("Photorec successfully finished")
