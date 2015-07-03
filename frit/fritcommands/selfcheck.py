#!/usr/bin/python
"""
selfcheck
This command is used to check if external tools are present on the system.
"""
import os
import fritutils

logger = fritutils.fritlog.loggers['selfcheckLog']

def selfcheck():
    logger.info('Starting selfcheck')
    for tool in fritutils.fritglobals.toolbox:
        if tool.check():
            fritutils.termout.printNormal('Tool "%s" found' % tool)
        else:
            fritutils.termount.printWarning('Tool "%s" NOT found' % tool)
