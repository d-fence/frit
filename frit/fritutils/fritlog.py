#!/usr/bin/python

import logging
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    filename='.frit/logs/frit-' +  str(os.getpid()) + '.log',
                    filemode='w')

loggers = {
        'getmailsLog' : logging.getLogger('frit.getmails'),
        'fritobjectsLog' : logging.getLogger('frit.fritobjects'),
        'hashesLog': logging.getLogger('frit.hashes'),
        }

def setLevels(level):
    if level == 'DEBUG':
        l = logging.DEBUG
    elif level == 'INFO':
        l = logging.INFO
    for logger in loggers:
        loggers[logger].setLevel(l)



