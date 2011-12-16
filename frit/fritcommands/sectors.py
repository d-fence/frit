#!/usr/bin/python
"""
sectors command
A command to extract unallocated sectors from a container
"""
import fritutils.termout
import fritutils.fritlog
import sys
import os.path

logger = fritutils.fritlog.loggers['sectorsLog']

def seclist(Evidences):
    """
    list subcommand. Print a list of unallocated sectors.
    We assume that sector size is 512 bytes. We will have to support variable
    sector sizes in a near future.
    """
    for evi in Evidences:
        secList = evi.getUnallocatedSectors()
        if secList:
            fritutils.termout.printSuccess('Unallocated sectors on "%s":' % evi.fileName)
            for u in secList:
                scount = u['end'] - u['start']
                ssize = fritutils.humanize(scount * 512)
                fritutils.termout.printNormal("\tStart: %d End: %s Count: %d Size: %s." % (u['start'],u['end'],scount,ssize))
        else:
            fritutils.termout.printWarning('No unallocated sectors found on "%s".' % evi.fileName)

def export(Evidences):
    """
    export unallocated sectors to .frit/extractions/unallocated/START-END/START-END.dd
    """
    for evi in Evidences:
        secList = evi.getUnallocatedSectors()
        if secList:
            for u in secList:
                endPath = "sectors_%d-%d" % (u['start'],u['end'])
                exportFile = endPath + '.dd'
                exportPath = os.path.join(evi.sectorsExportDir, endPath)
                if not os.path.exists(exportPath):
                    logger.info('Export path "%s" does not exist. Creating.' % exportPath)
                    os.makedirs(exportPath)
                exportFilePath = os.path.join(exportPath, exportFile)
                if os.path.exists(exportFilePath):
                    logger.error('Sectors file "%s" already exists, not exporting.' % exportFilePath)
                    fritutils.termout.printWarning('Sectors file "%s" already exists, not exporting.' % exportFilePath)
                else:
                    fritutils.termout.printMessage('Starting to export sectors from %d to %d' % (u['start'],u['end']))
                    logger.info('Starting to dump sectors %d - %d from %s' % (u['start'],u['end'],evi.fileName))
                    evi.ddump(u['start'],u['end'],exportFilePath)
                
def factory(Evidences,args,options):
    """
    args are the sectors command arguments
    """
    logger.info('Starting sectors command.')
    validArgs = ('list','export')
    if not args or len(args) == 0:
        fritutils.termout.printWarning('sectors command need at least an argument. Exiting.')
        logger.error('No argument given.')
        sys.exit(1)
    elif args[0] not in validArgs:
        fritutils.termout.printWarning('sectors command need a valid argument (%s)' % ', '.join(validArgs))
        logger.error('"%s" in not a valid arguement. Exiting.' % args[0])
        sys.exit(1)
    else:
        if args[0] == 'list':
            logger.info('list arguement given. Starting "sectors list" command.')
            seclist(Evidences)
        elif args[0] == 'export':
            logger.info('export arguement given. Starting "sectors export" command.')
            export(Evidences)

