#! /usr/bin/env python3
# TODO: probably better to rewrite the settings classes so that they
# return dicts, instead of the classes themselves
"""
Parses the .azk data files created by dmdx, and outputs a long format
csv file suitable for importing into R
"""
import re
import azksettings
import csv
import glob
import os
import sys
import textwrap


def yes_or_no(message):
    """"
    Takes a yes or no question as its argument, and asks for a response.
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
        print(textwrap.dedent(
        """
        AzkReader doesn't understand what you typed!
        Please type 'y' or 'n' only

        """
        )
        )
        # Recursive call to yes_or_no(), final response is passed up and
        # returned
        respond = yes_or_no(message)
    return respond


class AzkFiles:
    """
    Controller class that sets the input folder, gets the variable settings,
    creates the output file, and then creates an Azk() instance to process
    each individual .azk file
    Call this class to start the parsing process.
    """

    def __init__(self, azk_folder=None, conf_file=None):
        if azk_folder:
            self.azk_folder = azk_folder
        else:
            # Ask which folder the desired azk files are in
            self.azk_folder = self.get_azk_folder()
        # Create a list of all the azk files in that folder
        self.all_files = glob.glob(self.azk_folder + '/*.azk')

        if not conf_file is None:
            self.settings = azksettings.get_old_settings(filename=conf_file)
        else:
            use_old = yes_or_no("Use an existing settings file?")
            if use_old:
                self.settings = azksettings.get_old_settings()
            else:
                self.settings = azksettings.get_new_settings()
        self.outfile = open(
            self.settings.user_filename + '-output.csv',
            'w',
            newline=''
        )
        # Create the final output file here, and append to it when processing
        # each of the individual files
        output_fields = ['filename', 'subject', 'itemcode', 'rt', 'correct',
                         'trialnum']
        output_fields += [var for var in self.settings.code_vars]
        self.csv_out = csv.DictWriter(
            self.outfile,
            dialect='excel',
            fieldnames=output_fields
        )
        self.csv_out.writeheader()
        # Iteration through all the individual files happens here
        for azkfile in self.all_files:
            self.current_file = Azk(
                filename=azkfile,
                code_vars=self.settings.code_vars,
                output_file=self.csv_out
            )
        self.outfile.close()
        input("\n\nDone. Press ENTER to exit.")

    def get_azk_folder(self):
        """ 
        Prints a numbered list of the subfolders in the working directory (i.e.
        the directory the script is run from), and returns the directory the
        user chooses.
        """
        print(textwrap.dedent(
        """
        Which folder are your .azk files located in?
        If you cannot see them in this list, you need
        to copy the folder containing them to the
        same folder as this script.
        """
        )
        )
        dirs = [d for d in os.listdir() if os.path.isdir(d)] + ['EXIT']
        dir_dict = {ind: value for ind, value in enumerate(dirs)}
        for ind in dir_dict:
            print('(' + str(ind) + ') ' + dir_dict[ind])
        print('\n')
        resp = dir_dict[int(input())]
        if resp == 'EXIT':
            sys.exit()
        else:
            azk_files = glob.glob(resp + '/*.azk')
            while len(azk_files) == 0:
                print(textwrap.dedent(
                    """
                    ******************************************************
                    ERROR: No azk files found. Was that the right folder?
                    ******************************************************
                    """
                ))
                resp = self.get_azk_folder()
            return resp


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
        # split_filename: used to include the filename in the output
        self.split_filename = os.path.split(self.filename)[-1]
        self.inputfile = open(self.filename, 'r')
        self.file_subs = 0
        self.missing_subs = 0
        # Iteration through the file happens here
        for line in self.inputfile:
            self.identify_line_type(line)

    def identify_line_type(self, line):
        """
        Use regular expression matching to identify whether the
        current line is:

        * The line listing the total number of subjects in the file
        * The start of a new subject's results
        * The result of an individual trial, i.e. an item number and rt

        The regular expressions are defined as class variables,
        e.g. Azk.total_subs_re
        """
        line = line.strip()
        # Line indicating number of subjects that should be in the current file
        if Azk.total_subs_re.match(line):
            self.subs_should_be = int(line.split(' ')[-1])
        # Line indicating the start of a new subject's data
        elif Azk.new_sub_re.match(line):
            self.file_subs += 1
            self.look_for_id(line)
            self.current_trial = 0
        # Line with reaction time and response for an individual trial
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
        id_found = Azk.sub_id_re.search(line)
        if id_found:
            self.current_sub = id_found.group().split()[1]
        else:
            self.missing_subs += 1
            # Update the class variable, which persists across all instances,
            # and therefore keeps track of the total number of missing
            # subjects
            Azk.totalMissing += 1
            print('Subject ID missing in ', self.filename)
            self.current_sub = 'missing' + str(Azk.totalMissing)
            print('Replaced with ', self.current_sub)

    def process_trial(self, line):
        """
        Split the trial line into item number and rt, determine if the
        response was correct, and write all the data to the output file,
        including the current conditions as determined by code_vars.
        """
        splitline = line.split()
        code = str(splitline[0])
        rt = float(splitline[1])
        # Grab the COT, although it's not currently being used
        # try:
        #     cot = float(splitline[2])
        # except IndexError:
            # cot = None
        if rt > 0:
            correct = 1
        else:
            correct = 0
        rt = abs(rt)
        trial_info = {
            'filename': self.split_filename,
            'subject': self.current_sub,
            'itemcode': code,
            'rt': rt,
            'correct': correct,
            'trialnum': self.current_trial
        }
        # Segment the item number according to the user-defined variables
        for var in self.code_vars:
            current_slice = self.code_vars[var]
            trial_info[var] = code[current_slice]
        self.out.writerow(trial_info)


if __name__ == '__main__':
    # Start the whole thing with a call to AzkFiles
    parse = AzkFiles()
