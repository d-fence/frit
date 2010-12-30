#!/usr/bin/python

import logging
import fritutils.termout
import os
import sys

# We have to check if a .frit exists, if not, we assume that the init command
# was issued. So we log in the base directory
if os.path.exists('.frit'):
    if not os.path.exists('.frit/logs'):
        try:
            os.mkdir('.frit/logs')
        except:
            fritutils.termout.printWarning("Cannot create .frit/logs directory.")
            sys.exit(1)
    basepath = '.frit/logs/frit-'
else:
    basepath = './frit-'
    
        
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt ='%Y-%m-%d %H:%M:%S',
                    filename=basepath +  str(os.getpid()) + '.log',
                    filemode='w'
                    )

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
        }



def setLevels(level):
    if level == 'DEBUG':
        l = logging.DEBUG
    elif level == 'INFO':
        l = logging.INFO
    for logger in loggers:
        loggers[logger].setLevel(l)

