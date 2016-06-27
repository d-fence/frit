"""
Colorized output
"""

import sys
from colorama import init, Fore, Style

init()

def printWarning(s):
    print(Fore.RED + s.replace('\t', '    '))

def printSuccess(s):
    print(Fore.GREEN + s.replace('\t', '    '))

def printMessage(s):
    print(Fore.YELLOW + s.replace('\t', '    '))

def printNormal(s):
    print (s.replace('\t', '    '))
