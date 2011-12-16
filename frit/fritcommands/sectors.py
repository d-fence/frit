#!/usr/bin/python
"""
sectors command
A command to extract unallocated sectors from a container
"""
import fritutils.termout
import fritutils.fritlog

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

def factory(Evidences,args,options):
    """
    args are the sectors command arguments
    """
    logger.info('Starting sectors command.')
    validArgs = ('list')
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

