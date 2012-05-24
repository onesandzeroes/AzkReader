import os

class FolderBrowser:
    def goto_folder(self, message):
        print(message)
        indent = 0
        picked = False
        relpaths = []
        while not picked:
            if relpaths:
                relpath = os.path.join(*relpaths)
                dirs = [d for d in os.listdir(relpath) if os.path.isdir(relpath + os.sep + d)]
                print("Current folder: " + relpath)
            else:
                dirs = [d for d in os.listdir() if os.path.isdir(d)]
            dirs = dirs + ['DONE']
            if relpaths: 
                dirs = dirs + ['BACK']
            dir_dict = {ind: value for ind, value in enumerate(dirs)}
            for dir in dir_dict:
                print(' '*indent + '(' + str(dir) + ') ' + dir_dict[dir])
            resp = int(input())
            if dir_dict[resp] == 'DONE':
                picked = True
                return relpath
            elif dir_dict[resp] == 'BACK':
                relpaths.pop(-1)
                indent -= 2
            else:
                relpaths.append(dir_dict[resp])
                indent += 2