"""
browsers
This command is made to work on browsers.
find : will find the profiles pathes
...
"""
import fritutils
import os

CHROME_PATHES = (
    'Local Settings/Application Data/Chromium/User Data/Default',
    'Local Settings\Application Data\Google\Chrome\User Data\Default',
    'AppData\Local\Google\Chrome\User Data\Default',
    'AppData\Local\Chromium\User Data\Default',
    'Library/Application Support/Google/Chrome/Default',
    'Library/Application Support/Chromium/Default',
    '.config/google-chrome/Default',
    '.config/chromium/Default',
    )

logger = fritutils.fritlog.loggers['browsersLog']

class BrowserProfile(object):
    """
    Generic browser profile to be overriden by specific browser profiles
    """
    def __init__(self, profile_path):
        self.profile_path = profile_path

    def __str__(self):
        return 'Genereic browser'

class ChromeBrowser(BrowserProfile):
    """
    Object representing a chrome/chromium browser profile
    """

    def __init__(self, profile_path):
        super(ChromeBrowser, self).__init__(profile_path)

    def __str__(self):
        return 'Chrome browser profile : {}'.format(self.profile_path)

def find(Evidences, args):
    """
    Search for browser profiles and return an appropriate object
    """
    for evi in Evidences:
        fritutils.termout.printSuccess(
            "Searching for Browsers files in {}".format(evi.configName))
        for fs in evi.fileSystems:
            #TODO an option to search for custom locations
            for home_dir in fs.getHomeDirs():
                # Chrome and chromium
                if os.path.basename(home_dir) == 'chronos':
                    yield ChromeBrowser(home_dir)
                for chrome_path in CHROME_PATHES:
                    cfp = os.path.join(home_dir, chrome_path)
                    if os.path.isdir(cfp):
                        yield ChromeBrowser(cfp)

def factory(args):
    fritConfig = fritutils.getConfig()
    Evidences = fritutils.getEvidencesFromArgs(args, fritConfig)

    if args.cmd == 'find':
        logger.info('Starting find subcommand.')
        for browser in find(Evidences, args):
            fritutils.termout.printNormal(str(browser))
