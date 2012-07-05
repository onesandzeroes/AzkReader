import subprocess
import zipfile
import glob
import sys

subprocess.call(['C:/Python32/Scripts/cxfreeze.bat', 'azkreader.py', 
                 '--target-dir',  'CompiledExe'
                 ]
                 )



with zipfile.ZipFile('Downloads/AzkReader_win.zip', 'w') as zip_out:
    compiled_files = glob.glob('CompiledExe/*')
    for each in compiled_files:
        no_path = each.split('\\')[1]
        zip_out.write(each, 'AzkReader/' + no_path)
    #assert zip_out.testzip() == None