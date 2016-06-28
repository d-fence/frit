"""
Colorized output
"""

import sys
from colorama import init, Fore, Style

init()

def printWarning(s):
    print(Fore.RED + s.replace('\t', '    ') + Style.RESET_ALL)

def printSuccess(s):
    print(Fore.GREEN + s.replace('\t', '    ') + Style.RESET_ALL)

def printMessage(s):
    print(Fore.YELLOW + s.replace('\t', '    ') + Style.RESET_ALL)

def printNormal(s):
    print (Style.RESET_ALL + s.replace('\t', '    '))
