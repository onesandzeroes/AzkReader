import glob
import csv

# Rename 'thingsInID' to 'codeVars', 'indexesInID' to 'codeSlices'
class allSettings:
    codeVars = []
    codeSlices = []
    def createSlice(self, start, end):
        start, end = int(start), int(end)
        return slice(start, end)

# Leave out the 'Other' option for the moment, it's not really needed
class oldSettings(allSettings):
    found_confs = glob.glob('*.conf')
    def readOld(self):
        setting_csv = csv.DictReader(open(self.chosen_file), dialect='excel')
        for row in setting_csv:
            self.codeVars.append(row['variable'])
            index_slice = self.createSlice(row['start'], row['end'])
            self.codeSlices.append(index_slice)
    def askWhich(self):
        for optionNum, filename in enumerate(self.found_confs):
            print('(' + str(optionNum + 1) + ') ' + filename)
        fileChoice = int(input())
        self.chosen_file = self.found_confs[fileChoice - 1]
    def __init__(self):
        self.askWhich()
        self.readOld()
        self.userFilename = self.chosen_file.split('.')[0]
            
class newSettings(allSettings):
    codeIndexes = []
    def getVars(self):
        print("What variables need to be extracted from the ID number for each"
              " trial? Type them one at a time, then ENTER when you're done\n"
              )
        entered = input()
        while entered:
            self.codeVars.append(entered)
            entered = input()
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
    def writeSettings(self):
        filename = self.userFilename + '.conf'
        out = open(filename, 'w', newline='')
        csv_out = csv.writer(out, dialect='excel')
        csv_out.writerow(['variable', 'start', 'end'])
        zipped = zip(self.codeVars, self.codeIndexes)
        for i in zipped:
            csv_out.writerow([i[0], i[1][0], i[1][1]])
        out.close()
    def __init__(self):
        print("""
What should the settings file for this dataset be called?
(Just type a short name, e.g. the name of your experiment.
 Don't worry about the file extension, it gets added
 automatically)
"""
             )
        self.userFilename = input()
        self.getVars()
        self.indexes()
        self.writeSettings()
        
# Add some if __name__ = '__main__' tests down here