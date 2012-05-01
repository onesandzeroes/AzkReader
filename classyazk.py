#! /usr/bin/env python3

import re
import classysettings
import csv

def yesOrNo(message):
    print(message)
    print("(Y)es    (N)o")
    userResponse = str(input()).lower()
    if userResponse in ['y', 'yes']: 
        respond = True
    elif userResponse in ['n', 'no']:
        respond = False
    else:
        print("AzkReader doesn't understand what you typed!"
              "Please type 'y' or 'n' only\n")
        respond = yesOrNo(message)
    return respond    
            
# Not sure if this is the best way to choose an old or new file?            
useOld = yesOrNo("Use an existing settings file?")
if useOld:
    Settings = classysettings.oldSettings()
else:
    Settings = classysettings.newSettings()
   
