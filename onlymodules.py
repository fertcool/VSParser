import os
import re

import scanfiles


def launch():

    files = scanfiles.getsv(os.curdir)  # добавляем файлы всего проекта

    for file in files:

        fileopen = open(file, "r")
        filetext = fileopen.read()
        fileopen.close()

        modules = re.findall(r"module +[\w|\W]+?endmodule *: *\w+", filetext)

        if len(modules)>1:
            print(file)
        newtext = ''
        for module in modules:
            newtext = newtext + module + "\n"

        fileopen = open(file, "w")
        filetext = fileopen.write(newtext)
        fileopen.close()
