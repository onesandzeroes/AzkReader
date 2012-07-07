"""Classes to collect information about the variables reflected in
the experiment's item numbers, and the desired output filename"""
import glob
import csv

def create_slice(start, end):
    "Create a slice object that will be used to segment the item number"
    start, end = int(start), int(end)
    return slice(start, end)


class AllSettings:
    """Parent class that stores the variable names and indexes that will
    be used to segment the item number for each trial.
    """
    codeVars = []
    codeSlices = []
    
# Leave out the 'Other' option for the moment, it's not really needed
class OldSettings(AllSettings):
    """Called when the user is using an existing .conf file. """
    def read_old(self, filename):
        "Read info from the chosen settings file"
        setting_csv = csv.DictReader(open(filename), dialect='excel')
        for row in setting_csv:
            self.codeVars.append(row['variable'])
            index_slice = create_slice(row['start'], row['end'])
            self.codeSlices.append(index_slice)
    def ask_which(self):
        "List available settings files for user to choose"
        print("""Which settings file should be used?
              (if you can't see it, copy it to the same folder 
              as this script)""")
        for option_num, filename in enumerate(self.found_confs):
            print('(' + str(option_num + 1) + ') ' + filename)
        user_input = int(input())
        chosen_file = self.found_confs[user_input - 1]
        return chosen_file
    def __init__(self):
        self.found_confs = glob.glob('*.conf')
        use_file = self.ask_which()
        self.read_old(use_file)
        self.user_filename = use_file.split('.')[0]
            
class NewSettings(AllSettings):
    """Called when the information about the variables must be entered
    for the first time, creating a new .conf file"""
    codeIndexes = []
    def get_vars(self):
        """Ask about which variables/conditions are reflected 
        in the item numbers"""
        print("What variables need to be extracted from the ID number for each"
              " trial? Type them one at a time, then ENTER when you're done\n"
              )
        entered = input()
        while entered:
            self.codeVars.append(entered)
            entered = input()
    def indexes(self):
        "Get the locations of the variables within the item number"
        print("""Now type where those values are found in the item number.
              If they span multiple digits, type them in the form '2-4'.""")
        for var in self.codeVars:
            print(var)
            entered_index = str(input())
            if len(entered_index) > 1:
                start = int(entered_index.split('-')[0]) - 1
                end = int(entered_index.split('-')[1])
            else:
                start = int(entered_index) - 1
                end = start + 1
            self.codeIndexes.append((start, end))
        for pair in self.codeIndexes:
            self.codeSlices.append(create_slice(*pair))
    def write_settings(self):
        "Write the information about the variables to a .conf file"
        filename = self.user_filename + '.conf'
        out = open(filename, 'w', newline='')
        csv_out = csv.writer(out, dialect='excel')
        csv_out.writerow(['variable', 'start', 'end'])
        zipped = zip(self.codeVars, self.codeIndexes)
        for i in zipped:
            csv_out.writerow([i[0], i[1][0], i[1][1]])
        out.close()
    def __init__(self):
        print("""What should the settings file for this dataset be called?
        (Just type a short name, e.g. the name of your experiment.
        Don't worry about the file extension, it gets added
        automatically)""")
        self.user_filename = input()
        self.get_vars()
        self.indexes()
        self.write_settings()
        
# Add some if __name__ = '__main__' tests down here
