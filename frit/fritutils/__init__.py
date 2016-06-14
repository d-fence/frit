#!/usr/bin/python

import os
import os.path
import sys
import re
import configobj
import datetime
import containerprobe
import fritconf
import fritdb
import fritddump
import fritemails
import frithashes
import fritlog
import fritmmls
import fritmount
import fritobjects
import fritprobe
import fritundelete
import fritblkls
import fritcarving
import fritutils
import fsprobe
import pyloop
import termout

def getCommand(args):
    command = args[0]
    commandArgs = []
    options = []
    if len(args) > 1:
        commandArgs = args[1:]
        # here we force a list copy otherwise, when we remove the element from
        # the original list, the for loop is broken
        for a in list(commandArgs):
            if len(a) > 1 and (a[0]=='-' or a[:1]=='--'):
                options.append(a)
                commandArgs.remove(a)
    else:
        commandArgs= None
    if len(options) == 0:
        options = None
    return (command,commandArgs,options)

def noBadPath():
    """
    A function to check if the CWD is an allowed path to use it as a frit repository.
    """
    bad = False
    cwd = os.getcwd()
    badPathes = ('/','/home')
    badTrees = ('^/usr','^/var','^/etc','^/lib.*','^/boot','^/bin','^/sbin','^/proc','^/sys')
    for bt in badTrees:
        btr = re.compile(bt)
        if btr.search(cwd):
            bad = True

    if cwd in badPathes:
        bad = True

    if bad :
        fritutils.termout.printWarning("You cannot use frit from the '%s' directory" % cwd)
        sys.exit(1)

def isCwdFrit():
    """
    A function to check if there is already a .frit directory in CWD
    """
    cwd = os.getcwd()
    fritDir = os.path.join(cwd,'.frit')
    if os.path.exists(fritDir):
        return True
    else:
        return False

def humanize(x):
    """
    Function to convert a number of bytes in something more human readable
    """
    if x:
        units = { 'KiB': 1024, 'MiB': 1024*1024, 'GiB': 1024*1024*1024, 'TiB': 1024*1024*1024*1024 }
        r = "%d bytes" % x
        for u,v in units.items():
            if x < v:
                break
            r = "%d %s" % (x/v,u)
        return r
    else:
        return 0

def getOffset(offString):
    """
    A function to get the offset from the config "offset" string.
    It must return an integer representing the offset in bytes.
    offString can be a single number of bytes or a calculation
    """
    evalRe = re.compile('\+|\*|\-|\/')
    numRe = re.compile('^\d+$')
    if evalRe.search(offString):
        return eval(offString)
    elif numRe.search(offString):
        return int(offString)
    else:
        fritutils.termout.printWarning("Bad offset option !")
        sys.exit(1)

def unicodify(x):
    if not isinstance(x,unicode):
        try:
            y = unicode(x,'utf-8')
        except:
            print >> sys.stderr, "ERROR TRANSCODING %s TO UNICODE" % x
            y = x
        return y
    else:
        return x

def getBuffer(fname,pos,size):
    """
    Get a buffer from a filename starting at position pos
    with a size of size.
    """
    # should check if file exists first and what kind of filename
    fic = open(fname,"rb")
    fic.seek(pos)
    buf = fic.read(size)
    fic.close()
    return buf

def getConfig():
    """
    Check for a config file and return a config object.
    """
    if os.path.exists('.frit/config'):
        try:
            fritConfig = configobj.ConfigObj(
                '.frit/config',
                 indent_type='    ' )
        except configobj.ParseError,e:
            fritutils.termout.printWarning(
                'The config file contains error: {}'.format(e))
            sys.exit(1)
        except configobj.ConfigObjError:
            fritutils.termout.printWarning('The config file contains errors.')
            sys.exit(1)
    else:
        fritutils.termout.printWarning('No ".frit/config" found. Run "frit init" first."')
        sys.exit(1)
    return fritConfig

def startLog(command,logger):
    """
    Write a starting line in the log file
    command is the command issued
    return the start time of the command
    """
    logger.info('Starting %s command' % command)
    return(datetime.datetime.today())

def stopLog(command,startTime,logger):
    """
    Write a stop line in the log dfile with duration
    """
    diffTime = datetime.datetime.today() - startTime
    logger.info('%s command successfully ended in %s' % (command,diffTime))

def getEvidencesFromArgs(args,logger):
    """
    Try to map evidences given on the command line.
    Return a list of Evidence objects
    """
    Evidences = fritobjects.evidencesFromConfig(fritConfig, verbose=args.verbose)
    # Here we check if one ore more evidence names or evidence file names are
    # passed as an arguemnt, which means that the user only wants to work on
    # them
    if hasattr(args,'evidences'):
        specifiedEvidences = []
        for evi in Evidences:
            if evi.configName in args.evidences:
                args.remove(evi.configName)
                specifiedEvidences.append(evi)
            elif evi.fileName in args.evidences:
                args.remove(evi.fileName)
                specifiedEvidences.append(evi)
        if len(specifiedEvidences) > 0:
            Evidences = specifiedEvidences
            for evi in Evidences:
                logger.info('Working on evidence %s specified on command line' % evi.configName)
        else:
            logger.info('Working on all evidences.')
    return Evidences
