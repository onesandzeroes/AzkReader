import argparse
import azksettings
import azkreader

parser = argparse.ArgumentParser(description='Process azk files')
parser.add_argument(
    '--config-file',
    help='Configuration file outlining positions of variables in the item number',
    dest='conf_file',
    # make this argument required for now
    required=True
)
parser.add_argument(
    '--azk-folder',
    help='Folder containing the .azk files to be processed',
    dest='azk_folder',
    required=True
)

args = parser.parse_args()
azk_parse = azkreader.AzkFiles(
    azk_folder=args.azk_folder, 
    conf_file=args.conf_file
)
