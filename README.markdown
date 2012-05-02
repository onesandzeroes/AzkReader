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

It looks for the .azk files that DMDX produces in an 'Input' folder in the
folder the script is run from- for the new class-based version, both 
classyazk.py and classysettings.py need to be present in the same folder for 
it to work, as I haven't done any proper packaging.

The final file produced is a csv file, which should be easily importable into R
or the data analysis software of your choice.