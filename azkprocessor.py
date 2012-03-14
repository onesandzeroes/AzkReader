#! /usr/bin/env python3

import re
import glob
import csv

allAzks = glob.iglob('*.azk')

subjectsInFile = re.compile('Subjects\sincorporated')
subjectLine = re.compile('Subject\s[0-9]+')
IDsearch = re.compile('ID\s[0-9]+[a-zA-Z]+')
trialLine = re.compile('\s*[0-9]+\s+-*[0-9\.]+')



def askAboutSettings():
    print("Reuse settings from last time? \n (Y)es   (N)o")
    userResponse = str(input()).lower()
    if userResponse in ['y', 'yes']: 
        wantSettings = True
    elif userResponse in ['n', 'no']:
        wantSettings = False
    else:
        print("Unrecognised response! Please type 'y' or 'n' only\n")
        wantSettings = askAboutSettings()
    return wantSettings

def getNewSettings():
    global thingsInID
    global indexesInID
    writeSettingsFile = open("azkprocessor.conf", "w")
    print("What variables need to be extracted"
          " from the ID for each trial? Type them"
          " one at a time, then ENTER when you're done")
    thingsInID = []
    enteringIDthings = True
    while enteringIDthings == True:
        entered = input()
        if len(entered) > 0:
            thingsInID.append(entered)
        else: enteringIDthings = False
    print("Now type where those values are"
          " found in the ID string. \n" 
          "If they are longer than one digit,"
          " type them in the form '2-4' \n")
    indexesInID = []
    indexSettings = []
    for eachThing in thingsInID:
        print(str(eachThing))
        enteredIndex = str(input()) 
        if len(enteredIndex) > 1:
            start = int(enteredIndex.split('-')[0])-1
            end = int(enteredIndex.split('-')[1])
            indexesInID.append(slice(start,end))
        else:
            start = int(enteredIndex)-1
            end = int(enteredIndex)
            indexesInID.append(slice(start,end))
        indexSettings.append((start,end))        
    for i in range(0,len(thingsInID)):        
        writeSettingsFile.write(str(thingsInID[i]) + ',' + 
                                str(indexSettings[i][0]) + ',' + 
                                str(indexSettings[i][1]) + '\n')
    writeSettingsFile.close()

def getOldSettings():
    global thingsInID
    global indexesInID
    thingsInID=[]
    indexesInID = []
    for eachSetting in settingsFile:
        thingsInID.append(eachSetting[0])
        indexesInID.append(slice(int(eachSetting[1]),
                           int(eachSetting[2])))

## Looks for the settings file 'azkprocessor.conf', 
## and if it doesn't exist, creates it
try:
    settingsFile = csv.reader(open("azkprocessor.conf", "r"), 
                              dialect='excel')
    if askAboutSettings():
        getOldSettings()
    else:
        getNewSettings()
except IOError:
    getNewSettings()

##print("How long are your item ID codes?")
##IDLength = int(input())
## If the user doesn't want to reuse last time's settings, 
##  need to ask about the variables in the trial's ID number
##  and where they can be found
        

    
def grabTrialInfo(line,IDindexes):
    code = str(line.split()[0])
    rt = line.split()[1]
    if float(rt) > 0: correct = 1
    else: correct = 0
    trialInfo = [code, abs(float(rt)), correct, trialNum]
    for each in IDindexes:
        trialInfo.append(str(code[each]))
    return trialInfo

f = open('parsedAZK.csv', 'w', newline='')
outputFile = csv.writer(f, dialect='excel')
outputColumns = ['subject','itemcode','rt','correct','trialorder']
for thing in thingsInID:
    outputColumns.append(thing)
outputFile.writerow(outputColumns)

for eachFile in allAzks:
    currentFile = open(eachFile, 'r')
    subjectsDone = 0
    for line in currentFile:
        line = line.strip()
        if subjectsInFile.match(line):
            subjectsShouldBe = int(line.split(' ')[-1])
        elif subjectLine.match(line):
            subjectsDone += 1
            trialNum = 0
            currentSubject = IDsearch.search(line).group().split()[1]
        elif trialLine.match(line):
            trialNum += 1
            outputFile.writerow([currentSubject] + 
                                grabTrialInfo(line,indexesInID))
    if not subjectsDone == subjectsShouldBe:
        print("Number of subjects processed"
              " doesn't match what DMDX says it should be!")
    else: print("Number of subjects matches what's listed in the file")

f.close()
