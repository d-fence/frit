#!/usr/bin/python
"""
logs command.
Various commands to manipulate frit logs
"""
import os
import fritutils

logger = fritutils.fritlog.loggers['logsLog']

def showLogs():
    logger.info('Showing log files.')
    for logfile in os.listdir('.frit/logs'):
        fritutils.termout.printNormal(logfile)
        underline = '-' * len(logfile)
        fritutils.termout.printNormal(underline)
        logpath = os.path.join('.frit/logs',logfile)
        f = open(logpath,'r')
        text = f.read()
        fritutils.termout.printNormal(text)
        f.close()
        
def factory(Evidences,args):
    """
    args are the logs command arguments
    """
    logger.info('Starting logs command.')
    validArgs = ('show')
    if not args or len(args) == 0:
        fritutils.termout.printWarning('logs command need at least one argument. Exiting.')
        logger.error('No argument given.')
        sys.exit(1)
    elif args[0] not in validArgs:
        fritutils.termout.printWarning('logs command need a valid argument (%s)' % ', '.join(validArgs))
        logger.error('"%s" in not a valid arguement. Exiting.' % args[0])
        sys.exit(1)
    else:
        if args[0] == 'show':
            showLogs()
