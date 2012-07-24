#! /usr/bin/env python3
"""Parses the .azk data files created by dmdx, and outputs a long format
csv file suitable for importing into R
"""
import re
import azksettings
import csv
import glob
import os
import sys

def yes_or_no(message):
    """"Takes a yes or no question as its argument, and asks for a response.
    Will accept 'y', 'yes', 'n' or 'no', returning True or False as 
    appropriate. If it gets an unrecognized input, gives a warning and asks 
    again.
    """
    print(message)
    print("(Y)es    (N)o\n")
    user_response = str(input()).lower()
    if user_response in ['y', 'yes']: 
        respond = True
    elif user_response in ['n', 'no']:
        respond = False
    else:
        print("AzkReader doesn't understand what you typed!"
              "Please type 'y' or 'n' only\n")
        # Recursive call to yes_or_no(), final response is passed up and
        #returned
        respond = yes_or_no(message)
    return respond    
            

class AzkFiles:
    """Controller class that sets the input folder, gets the variable settings,
    creates the output file, and then creates an Azk() instance to process
    each individual .azk file
    Call this class to start the parsing process.
    """
    def __init__(self):
        # Ask which folder the desired azk files are in
        self.azk_folder = self.get_azk_folder()
        # Create a list of all the azk files in that folder
        self.all_files = glob.glob(self.azk_folder + '/*.azk')
        while len(self.all_files) == 0:
            print("\nERROR: No azk files found. Was that the right folder?")
            self.azk_folder = self.get_azk_folder()
            self.all_files = glob.glob(self.azk_folder + '/*.azk')
        use_old = yes_or_no("Use an existing settings file?")
        if use_old:
            self.settings = azksettings.OldSettings()
        else:
            self.settings = azksettings.NewSettings()
        self.outfile = open(self.settings.user_filename + '-output.csv',
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
                               [var for var in self.settings.code_vars]
                               )
        for each_file in self.all_files:
            self.current_file = Azk(each_file, 
                                    self.settings.code_vars,
                                    self.csv_out
                                    )
        self.outfile.close()
    def get_azk_folder(self):
        """ Print a numbered list of the subfolders in the working directory 
        (i.e. the directory the script is run from), and returns the directory 
        the user chooses.
        """
        print("""Which folder are your .azk files located in?
        If you cannot see them in this list, you need
        to copy the folder containing them to the
        same folder as this script. 
        """
        )
        dirs = [d for d in os.listdir() if os.path.isdir(d)] + ['EXIT']
        dir_dict = {ind: value for ind, value in enumerate(dirs)}
        for key in dir_dict:
            print('(' + str(key) + ') ' + dir_dict[key])
        print()
        resp = int(input())
        if dir_dict[resp] == 'EXIT':
            sys.exit()
        else:
            return dir_dict[resp]


class Azk:
    """
    Takes the filename of an azk file as input, and extracts the data from
    that file.
    """
    total_subs_re = re.compile('^Subjects\sincorporated')
    new_sub_re = re.compile('^Subject\s[0-9]+')
    trial_line_re = re.compile('\s*[0-9]+\s+-?[0-9]+\.[0-9]+')
    sub_id_re = re.compile('ID\s+[0-9a-zA-Z]+')
    # Set these as class variables so they can persist across the individual
    # instances
    totalSubs = 0
    totalMissing = 0
    def __init__(self, filename, code_vars, output_file):
        self.code_vars = code_vars
        self.out = output_file
        self.filename = filename
        self.inputfile = open(self.filename, 'r')
        self.file_subs = 0
        self.missing_subs = 0
        for line in self.inputfile:
            self.line_type(line)
    def line_type(self, line):
        """ Use regular expression matching to identify whether the 
        current line is:
        - The line listing the total number of subjects in the file
        - The start of a new subject's results
        - The result of an individual trial, i.e. an item number and rt
        The regular expressions are defined as class variables, 
        e.g. Azk.total_subs_re
        """
        line = line.strip()
        if Azk.total_subs_re.match(line):
            self.subs_should_be = int(line.split(' ')[-1])
        elif Azk.new_sub_re.match(line):
            self.file_subs += 1
            self.look_for_id(line)
            self.current_trial = 0
        elif Azk.trial_line_re.match(line):
            self.current_trial += 1
            self.process_trial(line)
    def look_for_id(self, line):
        """
        Takes the line identifying a new subject's results, and locates the
        alphanumeric subject ID. If not found, sets the subject ID to missingX,
        where X is the number of subjects with missing subject ID's in the 
        current run.
        """
        searched = Azk.sub_id_re.search(line)
        if searched:
            self.current_sub = searched.group().split()[1]
        else: 
            self.missing_subs += 1
            Azk.totalMissing += 1
            print('Subject ID missing in ' + self.filename)
            self.current_sub = 'missing' + str(Azk.totalMissing)
            print('Replaced with ' + self.current_sub)

    def process_trial(self, line):
        """
        Split the trial line into item number and rt, determine if the 
        response was correct, and write all the data to the output file,
        including the current conditions as determined by code_vars, code_slices
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
        trial_info = [self.current_sub, code, rt, correct, self.current_trial]
        # Segment the item number according to the user-defined variables
        for var in self.code_vars:
            current_slice = self.code_vars[var]
            trial_info.append(code[current_slice])
        self.out.writerow(trial_info)


if __name__ == '__main__':
    # Start the whole thing with a call to AzkFiles     
    parse = AzkFiles()
