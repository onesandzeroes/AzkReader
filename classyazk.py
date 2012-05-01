#! /usr/bin/env python3

import re
import glob
import csv

class YesNoQuestion:
    yes_no_text = "(Y)es      (N)o"
    response_dict = {'y': True, 'yes': True, 'n': False, 'no': False}
    def getAns(self):
        print(self.yes_no_text)
        response = input().lower()
        try:
            self.answer = self.response_dict[response]
        except KeyError:
            print("AzkReader doesn't understand what you typed!\n"
                  "Please type 'y' or 'n' only\n"
                  )
            self.getAns()
    def __init__(self, message):
        print(message)
        self.getAns()
# Rename 'thingsInID' to 'codeVars', 'indexesInID' to 'codeSlices'
class allSettings:
    codeVars = []
    codeSlices = []
    def createSlice(self, start, end):
        start, end = int(start), int(end)
        return slice(start, end)
    def readOld(self, filename):
        setting_csv = csv.reader(open(filename), dialect='excel')
        for row in setting_csv:
            self.codeVars.append(row['variable'])
            index_slice = self.createSlice(row['start'], row['end'])
            self.codeSlices.append(index_slice)

    found_confs = glob.glob('*.conf')

class newSettings(allSettings):
    codeIndexes = []
    def askUntilEmpty(self):
        entered = input()
        while entered:
            self.codeVars.append(entered)
            entered = input()
    def getNew(self):
        print("What should the settings file for this dataset be called?")
        self.userFilename = input()
        print("What variables need to be extracted from the ID number for each"
              "trial? Type them one at a time, then ENTER when you're done"
              )
        self.askUntilEmpty()
    def indexes(self):
        print("Now type where those values are found in the item number.\n"
              "If they span multiple digits, type them in the form '2-4'\n"
              )
        for var in self.codeVars:
            print(var)
            enteredIndex = str(input())
            if len(enteredIndex) > 1:
                start = int(enteredIndex.split('-')[0]) - 1
                end = int(enteredIndex.split('-')[1])
            else:
                start = int(enteredIndex) - 1
                end = start + 1
            self.codeIndexes.append((start, end))
        for pair in self.codeIndexes:
            self.codeSlices.append(self.createSlice(*pair))

           
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