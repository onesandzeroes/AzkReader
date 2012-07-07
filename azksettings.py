"""Classes to collect information about the variables reflected in
the experiment's item numbers, and the desired output filename"""
import glob
import csv

class OldSettings:
    """Called when the user is using an existing .conf file. """
    def read_old(self, filename):
        "Read info from the chosen settings file"
        setting_csv = csv.DictReader(open(filename), dialect='excel')
        for row in setting_csv:
            var = row['variable']
            start = int(row['start'])
            end = int(row['end'])
            self.code_vars[var] = slice(start, end)
    def ask_which(self):
        "List available settings files for user to choose"
        found_confs = glob.glob('*.conf')
        print("""Which settings file should be used?
              (if you can't see it, copy it to the same folder 
              as this script)""")
        for option_num, filename in enumerate(found_confs):
            print('(' + str(option_num + 1) + ') ' + filename)
        user_input = int(input())
        chosen_file = found_confs[user_input - 1]
        return chosen_file
    def __init__(self):
        self.code_vars = {}
        use_file = self.ask_which()
        self.read_old(use_file)
        self.user_filename = use_file.split('.')[0]
            
class NewSettings:
    """Called when the information about the variables must be entered
    for the first time, creating a new .conf file"""
    def get_vars(self):
        """Ask about which variables/conditions are reflected 
        in the item numbers"""
        print("What variables need to be extracted from the ID number for each"
              " trial? Type them one at a time, then ENTER when you're done\n"
              )
        self.input_vars = []
        entering = input()
        while entering:
            self.input_vars.append(entering)
            entering = input()
    def get_indexes(self):
        "Get the locations of the variables within the item number"
        print("""Now type where those values are found in the item number.
              If they span multiple digits, type them in the form '2-4'.""")
        self.input_indexes = {}
        for var in self.input_vars:
            print(var)
            entered_index = str(input())
            if len(entered_index) > 1:
                # Need to subtract one from the start to convert people's
                # indexing (which starts from 1) to Python's (which starts 
                # from 0)
                start = int(entered_index.split('-')[0]) - 1
                end = int(entered_index.split('-')[1])
            else:
                start = int(entered_index) - 1
                end = start + 1
            self.code_vars[var] = slice(start, end)
            # Create tuples containing the indexes to save in the conf file
            self.input_indexes[var] = (start, end)
    def write_settings(self):
        "Write the information about the variables to a .conf file"
        filename = self.user_filename + '.conf'
        out = open(filename, 'w', newline='')
        csv_out = csv.writer(out, dialect='excel')
        csv_out.writerow(['variable', 'start', 'end'])
        for var in self.input_indexes:
            start = self.input_indexes[var][0]
            end   = self.input_indexes[var][1]
            csv_out.writerow([var, start, end])
        out.close()
    def __init__(self):
        self.code_vars = {}
        print("""What should the settings file for this dataset be called?
        (Just type a short name, e.g. the name of your experiment.
        Don't worry about the file extension, it gets added
        automatically)""")
        self.user_filename = input()
        self.get_vars()
        self.get_indexes()
        self.write_settings()
        
# Add some if __name__ = '__main__' tests down here
