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
   
class AzkFiles:
    totalSubs_re = re.compile('Subjects\sincorporated')
    newSub_re = re.compile('Subject\s[0-9]+')
    trialLine_re = re.compile('\s*[0-9]+\s+-*[0-9\.]+')
    totalSubs = 0
    totalMissing = 0
    allFiles = glob.iglob('*.azk')
    def __init__(self):
        for eachFile in allFiles:
            current = Azk(eachfile)

class Azk(AzkFiles):
    subID_re = re.compile('ID\s*[0-9a-zA-Z]+')
    def lookforID(self, line):
        searched = self.subID_re.search(dmdxLine)
        if searched:
            subID = searched.group().split()[1]
        else: 
            AzkFiles.totalMissing += 1
            print('Subject ID missing in ' + self.filename)
            subID = 'missing' + str(AzkFiles.totalMissing)
            print('Replaced with ' + subID)
    def lineType(self, line):
        line = line.strip()
        if totalSubs_re.match(line):
            self.SubsShouldBe = int(line.split(' ')[-1])
        elif newSub_re.match(line):
            self.fileSubs += 1
            self.currentSub = self.lookForID(line)
            self.currentTrial = 0
        elif trialLine.match(line):
            self.currentTrial += 1
            
            
    def __init__(self, filename):
        self.filename = filename
        self.fileSubs = 0
        self.currentTrial = 0

class trialLine