AzkReader
=========

This is a short Python script intended to make it easy to export data from DMDX
directly into the "long" data format that works best for R. It also retains 
information about the order items were presented in, which can be useful for
some analyses. 

It currently runs as a terminal/command line application that asks you about
how your variables are encoded in the DMDX item numbers. Since this is a
bit tedious, it saves this information to settings file. 

It looks for the .azk files that DMDX produces in the folder the script is run 
from- until this is changed, it's best to copy the script to the folder that
contains *all* the .azk files for your experiment, and run it from there.

The final file produced is a csv file, which should be easily importable into R
or the data analysis software of your choice.