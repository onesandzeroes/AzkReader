"""Classes to collect information about the variables reflected in
the experiment's item numbers, and the desired output filename"""
import glob
import csv
import collections
import textwrap


def get_old_settings(filename=None):
    """
    Reads a configuration file that specifies the variables
    reflected in the DMDX item codes and their positions.
    `filename` is either directly specified as an argument,
    or the user is asked which file to use.
    Returns a dict with two elements, "user_filename" and
    "code_vars", which are used to determine the output
    filename and the information extracted from the trials.
    """
    res = {}
    # code_vars = collections.OrderedDict()
    if filename is None:
        filename = ask_which_conf_file()
    res['user_filename'] = filename.split('.')[0]
    res['code_vars'] = read_conf_file(filename)
    return res

def ask_which_conf_file():
    "List available settings files for user to choose"
    found_confs = glob.glob('*.conf')
    print(textwrap.dedent(
    """
    Which settings file should be used?
    (if you can't see it, copy it to the same folder
    as this script, or just create a new one)
    """
    )
    )
    for option_num, filename in enumerate(found_confs):
        print('(' + str(option_num + 1) + ') ' + filename)
    user_input = int(input())
    chosen_file = found_confs[user_input - 1]
    return chosen_file

def read_conf_file(filename):
    "Read info from the chosen settings file"
    code_vars = collections.OrderedDict()
    setting_csv = csv.DictReader(open(filename), dialect='excel')
    for row in setting_csv:
        var = row['variable']
        start = int(row['start'])
        end = int(row['end'])
        code_vars[var] = slice(start, end)
    return code_vars


def get_new_settings():
    """
    Asks the user about the variables that are reflected in the DMDX
    item codes, and their positions. 
    Returns a two element dictionary, containing "user_filename" and
    "code_vars"
    """
    res = {}
    print(textwrap.dedent(
    """
    What should the settings file for this dataset be called?
    (Just type a short name, e.g. the name of your experiment.
    Don't worry about the file extension, it gets added
    automatically)
    """
    )
    )
    res['user_filename'] = input()
    code_tuples = get_new_vars()
    write_new_settings(res['user_filename'], code_tuples)
    res['code_vars'] = create_slices(code_tuples)
    return res

def get_new_vars():
    """
    Ask about which variables/conditions are reflected
    in the item numbers, and pass them to get_new_indexes
    to find out their locations/digits
    """
    print(textwrap.dedent(
    """
    What variables need to be extracted from the ID number for each
    trial? Type them one at a time, then ENTER when you're done
    """
    )
    )
    input_vars = []
    entering = input()
    while entering:
        input_vars.append(entering)
        entering = input()
    code_tuples = get_new_indexes(input_vars)
    return code_tuples

def get_new_indexes(input_vars):
    """
    Get the locations of the variables within the item number.
    Note: because this script is designed to be used by people
    who aren't necessarily familiar with Python, indexing is
    1-based instead of 0-based
    """
    print(textwrap.dedent(
    """
    Now type where those values are found in the item number.
    e.g. If your item number is 153, and the value for prime_type
    is 5, then prime_type is found at position 2, so
    enter 2 for that variable.
    If they span multiple digits, type them in the form '2-4'.
    """
    )
    )
    code_tuples = collections.OrderedDict()
    for var in input_vars:
        entered_index = input()
        # Sometimes variables span multiple digits, and the user enters them
        # in the form "2-5"
        if len(entered_index) > 1:
            # Need to subtract one from the start to convert people's indexing
            # (which starts from 1) to Python's (which starts from 0)
            start = int(entered_index.split('-')[0]) - 1
            end = int(entered_index.split('-')[1])
        else:
            start = int(entered_index) - 1
            end = start + 1
        code_tuples[var] = (start, end)
    return code_tuples

def create_slices(code_tuples):
    """
    Convert the tuples specifying start and end digits for
    the variables into slice objects
    """
    code_vars = collections.OrderedDict()
    for var in code_tuples:
        code_vars[var] = slice(*code_tuples[var])
    return code_vars

def write_new_settings(filename, code_tuples):
    "Write the information about the variables to a .conf file"
    filename = filename + '.conf'
    with open(filename, 'w', newline='') as out:
        csv_out = csv.writer(out, dialect='excel')
        csv_out.writerow(['variable', 'start', 'end'])
        for var in code_tuples:
            start = code_tuples[var][0]
            end = code_tuples[var][1]
            csv_out.writerow([var, start, end])
        out.close()

class NewSettings:
    """
    Called when the information about the variables must be entered
    for the first time, creating a new .conf file
    """
    def __init__(self):
        self.code_vars = collections.OrderedDict()
        print(textwrap.dedent(
        """
        What should the settings file for this dataset be called?
        (Just type a short name, e.g. the name of your experiment.
        Don't worry about the file extension, it gets added
        automatically)
        """
        )
        )
        self.user_filename = input()
        self.get_vars()
        self.get_indexes()
        self.write_settings()

    def get_vars(self):
        """
        Ask about which variables/conditions are reflected
        in the item numbers
        """
        print(textwrap.dedent(
        """
        What variables need to be extracted from the ID number for each
        trial? Type them one at a time, then ENTER when you're done
        """
        )
        )
        self.input_vars = []
        entering = input()
        while entering:
            self.input_vars.append(entering)
            entering = input()

    def get_indexes(self):
        """
        Get the locations of the variables within the item number.
        Note: because this script is designed to be used by people
        who aren't necessarily familiar with Python, indexing is
        1-based instead of 0-based
        """
        print(textwrap.dedent(
        """
        Now type where those values are found in the item number.
        e.g. If your item number is 153, and the value for prime_type
        is 5, then prime_type is found at position 2, so
        enter 2 for that variable.
        If they span multiple digits, type them in the form '2-4'.
        """
        )
        )
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
            end = self.input_indexes[var][1]
            csv_out.writerow([var, start, end])
        out.close()


if __name__ == '__main__':
    test_old = get_old_settings(filename="new_test.conf")
    assert(test_old == {
        'code_vars': collections.OrderedDict(
            [('item_number', slice(0, 3, None)),
             ('prime_type', slice(3, 4, None)),
             ('target_freq', slice(4, 5, None))]
        ),
        'user_filename': 'new_test'
    }
    )
    print(test_old)
    test_new = get_new_settings()
    print(test_new)
