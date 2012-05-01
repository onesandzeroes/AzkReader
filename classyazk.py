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
   
# Change the conf files to have a header, use DictReader to parse them,
# i.e.
# def writeSettingsFile(filename, things, indexes):
    # settingsFile = csv.writer(open(filename + '.conf', 'w', newline=''), 
                              # dialect='excel'
                              # )
    # settingsFile.writerow(['variable', 'start', 'end'])
    # zipped = zip(things, indexes)
    # for i in zipped:
        # settingsFile.writerow([i[0], i[1][0], i[1][1]])