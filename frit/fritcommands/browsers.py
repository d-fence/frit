"""
browsers
This command is made to work on browsers.
find : will find the profiles pathes
...
"""

def find():
    pass

def factory(args):
    fritConfig = fritutils.getConfig()
    Evidences = fritutils.getEvidencesFromArgs(args, fritConfig)

    if args.cmd == 'find':
        find(Evidences, args)
