#!/usr/bin/python

import logging
import os

if not os.path.exists('.frit/logs'):
    try:
        os.mkdir('.frit/logs')
    except:
        fritutils.termout.printWarning("Cannot create .frit/logs directory.")
        sys.exit(1)
        
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    filename='.frit/logs/frit-' +  str(os.getpid()) + '.log',
                    filemode='w')

loggers = {
        'mainfritLog' : logging.getLogger('frit.mainfrit'),
        'getmailsLog' : logging.getLogger('frit.getmails'),
        'fritobjectsLog' : logging.getLogger('frit.fritobjects'),
        'hashesLog': logging.getLogger('frit.hashes'),
        'undeleteLog': logging.getLogger('frit.undelete'),
        }



def setLevels(level):
    if level == 'DEBUG':
        l = logging.DEBUG
    elif level == 'INFO':
        l = logging.INFO
    for logger in loggers:
        loggers[logger].setLevel(l)



