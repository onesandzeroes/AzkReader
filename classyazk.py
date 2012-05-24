#! /usr/bin/env python3

import re
import classysettings
import csv
import glob
import os
from sys import exit

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
# Update: Seems a bit more sensible now
class AzkFiles:
    def __init__(self):
        self.get_azk_folder()
        self.allFiles = glob.iglob(self.azk_folder + '/*.azk')
        self.useOld = yesOrNo("Use an existing settings file?")
        if self.useOld:
            self.Settings = classysettings.oldSettings()
        else:
            self.Settings = classysettings.newSettings()
        self.outfile = open(self.Settings.userFilename + '-output.csv',
                            'w', 
                            newline=''
                            )
        self.csv_out = csv.writer(self.outfile, dialect='excel')
        self.csv_out.writerow(['subject', 
                               'itemcode', 
                               'rt', 
                               'correct', 
                               'trialnum'] +
                               self.Settings.codeVars
                               )
        for eachFile in self.allFiles:
            self.current = Azk(eachFile, self)
        self.outfile.close()
    def get_azk_folder(self):
        print("""
Which folder are your .azk files located in?
If you cannot see them in this list, you need
to copy the folder containing them to the
same folder as this script. 
"""
        )
        dirs = [d for d in os.listdir() if os.path.isdir(d)] + ['EXIT']
        dir_dict = {ind: value for ind, value in enumerate(dirs)}
        for x in range(len(dir_dict)):
            print('(' + str(x) + ') ' + dir_dict[x])
        resp = int(input())
        if dir_dict[resp] == 'EXIT':
            exit()
        else:
            self.azk_folder = dir_dict[resp]
        
        
        
# The way I'm currently coding this, it needs an AzkInstance passed in so
# it can read the settings and find the output file. Shouldn't be too clunky 
# since it only needs one call to AzkFiles to run the whole thing 
class Azk:
    totalSubs_re = re.compile('Subjects\sincorporated')
    newSub_re = re.compile('Subject\s[0-9]+')
    trialLine_re = re.compile('\s*[0-9]+\s+-*[0-9\.]+')
    subID_re = re.compile('ID\s*[0-9a-zA-Z]+')
    totalSubs = 0
    totalMissing = 0
    def __init__(self, filename, AzkInstance):
        self.codeVars = AzkInstance.Settings.codeVars
        self.codeSlices = AzkInstance.Settings.codeSlices
        self.out = AzkInstance.csv_out
        self.filename = filename
        self.fileSubs = 0
        self.missingSubs = 0
        self.inputfile = open(self.filename, 'r')
        for line in self.inputfile:
            line = line.strip()
            self.lineType(line)
    def lookForID(self, line):
        searched = Azk.subID_re.search(line)
        if searched:
            self.currentSub = searched.group().split()[1]
        else: 
            self.missingSubs += 1
            Azk.totalMissing += 1
            print('Subject ID missing in ' + self.filename)
            self.currentSub = 'missing' + str(Azk.totalMissing)
            print('Replaced with ' + self.currentSub)
    def lineType(self, line):
        line = line.strip()
        if Azk.totalSubs_re.match(line):
            self.SubsShouldBe = int(line.split(' ')[-1])
        elif Azk.newSub_re.match(line):
            self.fileSubs += 1
            self.lookForID(line)
            self.currentTrial = 0
        elif Azk.trialLine_re.match(line):
            self.currentTrial += 1
            self.processTrial(line)
    def processTrial(self, line):
        splitline = line.split()
        code = str(splitline[0])
        rt = float(splitline[1])
        if rt > 0:
            correct = 1
        else:
            correct = 0
        rt = abs(rt)
        trialInfo = [self.currentSub, code, rt, correct, self.currentTrial]
        for eachslice in self.codeSlices:
            trialInfo.append(code[eachslice])
        self.out.writerow(trialInfo)
        
if __name__ == '__main__':
    # Start the whole thing with a call to AzkFiles     
    parse = AzkFiles()