#! /usr/bin/env python3

import re
import azksettings
import csv
import glob
import os
from sys import exit

def yesOrNo(message):
    """"
Takes a yes or no question as its argument, and asks for a response.
Will accept 'y', 'yes', 'n' or 'no', returning True or False as appropriate.
If it gets an unrecognized input, gives a warning and asks again
    """
    print(message)
    print("(Y)es    (N)o\n")
    userResponse = str(input()).lower()
    if userResponse in ['y', 'yes']: 
        respond = True
    elif userResponse in ['n', 'no']:
        respond = False
    else:
        print("AzkReader doesn't understand what you typed!"
              "Please type 'y' or 'n' only\n")
        # Recursive call to yesOrNo(), final response is passed up and
        #returned
        respond = yesOrNo(message)
    return respond    
            

class AzkFiles:
    def __init__(self):
        # Ask which folder the desired azk files are in
        self.get_azk_folder()
        #Check that there actually are azk files in there
        self.check_Azk = glob.glob(self.azk_folder + '/*.azk')
        while len(self.check_Azk) == 0:
            print("\nERROR: No azk files found. Was that the right folder?")
            self.get_azk_folder()
            self.check_Azk = glob.glob(self.azk_folder + '/*.azk')
        # Create a list of all the azk files in that folder
        self.allFiles = glob.iglob(self.azk_folder + '/*.azk')
        self.useOld = yesOrNo("Use an existing settings file?")
        if self.useOld:
            self.Settings = azksettings.oldSettings()
        else:
            self.Settings = azksettings.newSettings()
        self.outfile = open(self.Settings.userFilename + '-output.csv',
                            'w', 
                            newline=''
                            )
        # Create the final output file here, and append to it when processing
        # each of the individual files
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
        """ 
Print a numbered list of the subfolders in the working directory (i.e. the
directory the script is run from), and set the input folder to the
directory the user chooses.
Doesn't actually return anything, just sets self.azk_folder.
"""
        print("""
Which folder are your .azk files located in?
If you cannot see them in this list, you need
to copy the folder containing them to the
same folder as this script. 
"""
        )
        dirs = [d for d in os.listdir() if os.path.isdir(d)] + ['EXIT']
        dir_dict = {ind: value for ind, value in enumerate(dirs)}
        for x in dir_dict:
            print('(' + str(x) + ') ' + dir_dict[x])
        print()
        resp = int(input())
        if dir_dict[resp] == 'EXIT':
            exit()
        else:
            self.azk_folder = dir_dict[resp]
        
        
        
# The way I'm currently coding this, it needs an AzkInstance passed in so
# it can read the settings and find the output file. Shouldn't be too clunky 
# since it only needs one call to AzkFiles to run the whole thing 
class Azk:
    totalSubs_re = re.compile('^Subjects\sincorporated')
    newSub_re = re.compile('^Subject\s[0-9]+')
    trialLine_re = re.compile('\s*[0-9]+\s+-?[0-9]+\.[0-9]+')
    subID_re = re.compile('ID\s+[0-9a-zA-Z]+')
    # Set these as class variables so they can persist across the individual
    # instances
    totalSubs = 0
    totalMissing = 0
    def __init__(self, filename, AzkInstance):
        self.codeVars = AzkInstance.Settings.codeVars
        self.codeSlices = AzkInstance.Settings.codeSlices
        self.out = AzkInstance.csv_out
        self.filename = filename
        self.inputfile = open(self.filename, 'r')
        self.fileSubs = 0
        self.missingSubs = 0
        for line in self.inputfile:
            self.lineType(line)
    def lineType(self, line):
        """
Use regular expression matching to identify whether the current line is:
    - The line listing the total number of subjects in the file
    - The start of a new subject's results
    - The result of an individual trial, i.e. an item number and rt
The regular expressions are defined as class variables, e.g. Azk.totalSubs_re
"""
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
    def lookForID(self, line):
        """
Takes a line identifying a new subject's results, and locates the
alphanumeric subject ID. If not found, sets the subject ID to missingX,
where X is the number of subjects with missing subject ID's in the current 
run.
"""
        searched = Azk.subID_re.search(line)
        if searched:
            self.currentSub = searched.group().split()[1]
        else: 
            self.missingSubs += 1
            Azk.totalMissing += 1
            print('Subject ID missing in ' + self.filename)
            self.currentSub = 'missing' + str(Azk.totalMissing)
            print('Replaced with ' + self.currentSub)

    def processTrial(self, line):
        """
Split the trial line into item number and rt, determine if the response was
correct, and write all the data to the output file, including the current
conditions as determined by codeVars, codeSlices
"""
        splitline = line.split()
        code = str(splitline[0])
        rt = float(splitline[1])
        # Grab the COT, although it's not currently being used
        try:
            cot = float(splitline[2])
        except IndexError:
            cot = None
        if rt > 0:
            correct = 1
        else:
            correct = 0
        rt = abs(rt)
        trialInfo = [self.currentSub, code, rt, correct, self.currentTrial]
        # Segment the item number according to the user-defined variables
        for eachslice in self.codeSlices:
            trialInfo.append(code[eachslice])
        self.out.writerow(trialInfo)
        
if __name__ == '__main__':
    # Start the whole thing with a call to AzkFiles     
    parse = AzkFiles()