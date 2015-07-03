#!/usr/bin/python

import logging
import fritutils.termout
import os
import sys

def setLevels(level):
    if level == 'DEBUG':
        l = logging.DEBUG
    elif level == 'INFO':
        l = logging.INFO
    for logger in loggers:
        loggers[logger].setLevel(l)

logFile = '.frit/logs/frit-' + str(os.getpid()) + '.log'
logFormat = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

loggers = {
        'mainfritLog' : logging.getLogger('frit.mainfrit'),
        'getmailsLog' : logging.getLogger('frit.getmails'),
        'fritobjectsLog' : logging.getLogger('frit.fritobjects'),
        'hashesLog': logging.getLogger('frit.hashes'),
        'undeleteLog': logging.getLogger('frit.undelete'),
        'logsLog' : logging.getLogger('frit.logs'),
        'mountLog' : logging.getLogger('frit.mount'),
        'fritmountLog' : logging.getLogger('frit.fritmount'),
        'extensionsLog': logging.getLogger('frit.extensions'),
        'storeLog' : logging.getLogger('frit.store'),
        'sectorsLog' : logging.getLogger('frit.sectors'),
        'selfcheckLog' : logging.getLogger('frit.selfcheck'),
        'globalsLog' : logging.getLogger('frit.fritglobals'),
        'getunallocLog' : logging.getLogger('frit.getunalloc'),
        'carvingLog': logging.getLogger('frit.carving'),
        }

# Configuring default level to INFO
for l in loggers:
    loggers[l].setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormat)

# We have to check if a .frit exists, if not, we assume that the init command
# was issued. So we log to the console
if os.path.exists('.frit'):
    if not os.path.exists('.frit/logs'):
        try:
            os.mkdir('.frit/logs')
        except:
            fritutils.termout.printWarning("Cannot create .frit/logs directory.")
            sys.exit(1)
    fileHandler = logging.FileHandler(filename=logFile,encoding='utf8')
    fileHandler.setFormatter(logFormat)
    for l in loggers:
        loggers[l].addHandler(fileHandler)
else:
    for l in loggers:
        loggers[l].addHandler(consoleHandler)

