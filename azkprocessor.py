#! /usr/bin/env python3

import re
import glob
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


def getNewSettings():
    global thingsInID
    global indexesInID
    global userFilename
    print("What should the settings file for this dataset be called?")
    userFilename = input()
    settingsFilename = userFilename + '.conf'
    writeSettingsFile = open(settingsFilename, "w")
    print("What variables need to be extracted"
          " from the ID for each trial? Type them"
          " one at a time, then ENTER when you're done")
    thingsInID = []
    enteringIDthings = True
    while enteringIDthings == True:
        entered = input()
        if len(entered) > 0:
            thingsInID.append(entered)
        else:
            enteringIDthings = False
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
            start = int(enteredIndex.split('-')[0]) - 1
            end = int(enteredIndex.split('-')[1])
            indexesInID.append(slice(start, end))
        else:
            start = int(enteredIndex) - 1
            end = int(enteredIndex)
            indexesInID.append(slice(start, end))
        indexSettings.append((start, end))
    for i in range(0, len(thingsInID)):
        writeSettingsFile.write(str(thingsInID[i]) + ',' +
                                str(indexSettings[i][0]) + ',' +
                                str(indexSettings[i][1]) + '\n')
    writeSettingsFile.close()

def getOldSettings(filename):
    global thingsInID
    global indexesInID
    settingsFile = csv.reader(open(filename), dialect='excel')
    thingsInID=[]
    indexesInID = []
    for eachSetting in settingsFile:
        thingsInID.append(eachSetting[0])
        indexesInID.append(slice(int(eachSetting[1]),
                           int(eachSetting[2])))
                         
def askWhichFile():
    global userFilename
    # Replace this with a gui file picker at some point
    print("Which settings file do you want to use?")
    existingConfs = glob.glob('*.conf')
    existingConfs.append('Other')
    for optionNum, filename in enumerate(existingConfs):
        print('(' + str(optionNum + 1) + ') ' + filename)
    userInput = int(input())
    chosenFilename = existingConfs[(userInput - 1)]
    if chosenFilename == 'Other':
        print("What is the name of the settings file you want to use?")
        print("(Leave out the .conf extension)")
        userFilename = input()
        getOldSettings(userFilename + '.conf')
    else:
        userFilename = chosenFilename[:-5]
        getOldSettings(chosenFilename)


    
def grabTrialInfo(dmdxLine, IDindexes, trialNum):
    code = str(dmdxLine.split()[0])
    rt = dmdxLine.split()[1]
    if float(rt) > 0:
        correct = 1
    else:
        correct = 0
    trialInfo = [code, abs(float(rt)), correct, trialNum]
    for each in IDindexes:
        trialInfo.append(str(code[each]))
    return trialInfo
    
def lookForID(dmdxLine, filename):
    global missingIDs
    IDsearch = re.compile('ID\s*[0-9a-zA-Z]+')
    searched = IDsearch.search(dmdxLine)
    if searched:
        subID = searched.group().split()[1]
    else: 
        missingIDs += 1
        print('Subject ID missing in ' + filename)
        subID = 'missing' + str(missingIDs)
        print('Replaced with ' + subID)
    return subID
    
def parseFile(filename):
    global missingIDs
    subjectsInFile = re.compile('Subjects\sincorporated')
    subjectLine = re.compile('Subject\s[0-9]+')
    trialLine = re.compile('\s*[0-9]+\s+-*[0-9\.]+')
    currentFile = open(filename)
    subjectsDone = 0
    for line in currentFile:
        line = line.strip()
        if subjectsInFile.match(line):
            subjectsShouldBe = int(line.split(' ')[-1])
        elif subjectLine.match(line):
            subjectsDone += 1
            trialNumber = 0
            currentSubject = lookForID(line, filename)
        elif trialLine.match(line):
            trialNumber += 1
            trialInfo = grabTrialInfo(line, indexesInID, trialNumber)
            outputFile.writerow([currentSubject] + trialInfo)
    if not subjectsDone == subjectsShouldBe:
        print("Number of subjects processed"
              " doesn't match what DMDX says it should be!")
    else:
        print("Number of subjects matches what's listed in the file")


existingSettings = yesOrNo("Use an existing settings file?")
if existingSettings:
    askWhichFile()
else:
    getNewSettings()

f = open(userFilename + '.csv', 'w', newline='')
outputFile = csv.writer(f, dialect='excel')
outputColumns = ['subject', 'itemcode', 'rt', 'correct', 'trialorder']
for thing in thingsInID:
    outputColumns.append(thing)
outputFile.writerow(outputColumns)


allAzks = glob.iglob('*.azk')
for eachFile in allAzks:
    missingIDs = 0
    parseFile(eachFile)

f.close()
