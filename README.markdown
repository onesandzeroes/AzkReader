AzkReader
=========

This is a short Python script intended to make it easy to export data from DMDX
directly into the "long" data format that works best for R. It also retains 
information about the order items were presented in, which can be useful for
some analyses. 

It currently runs as a terminal/command line application that asks you about
how your variables are encoded in the DMDX item numbers. Since this is a
bit tedious, it saves this information to a settings file so you can repeat
the process later. 

Both the *azkreader.py* and *azksettings.py* scripts are required, and must
be located in the same folder.

Or, you can download an executable version of the program 
[here](https://github.com/onesandzeroes/AzkReader/raw/master/Downloads/AzkReader_win.zip).

When running the script, put all of your .azk files from a 
single experiment/list in a single folder, then move that folder to the 
same directory as the *azkreader.py* script. The program will ask you which 
sub-directory your files are located in, then process all of those files in 
one go, giving you a single output file.

The final file produced is a csv file, which should be easily importable into R
or the data analysis software of your choice.