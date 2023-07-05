import os
import re


# поиск всех sv файлов в директории и поддиректориях
def scan(dir, svfiles):

    # dirfiles = []  # все файлы и папки директории
    dirpathes = []  # все папки директории

    # сканирование файлов
    with os.scandir(dir) as files:
        for file in files:

            # добавление файла или папки в список
            # dirfiles.append(dir + "\\" + file.name)

            # добавление файла sv в список
            if file.name.endswith(".sv"):
                svfiles.append(dir + "\\" + file.name)

            # добавление подкаталогов(папок) с список
            if file.is_dir():
                dirpathes.append(file.name)

    # идем дальше по всем папкам в текущей дериктории
    for path in dirpathes:
        scan(dir + "\\" + path, svfiles)


# получить список sv файлов
def getsv(dir):
    svfiles = []  # список путей sv файлов
    scan(dir, svfiles)
    return svfiles

def getallmodules(dir):

    # перед поиском желательно удалить все комментарии и выполнить обработку ifdef/ifndef
    # можно использовать obfuscator.preobfuscator()

    svfiles = getsv(dir)  # список путей sv файлов

    modules = {}  # словарь модулей во всем проекте, где ключ - название модуля, а значение - список его портов

    for svfile in svfiles:
        getmodules_infile(svfile, modules)

    return modules

def getmodules_infile(file, modules):
    fileopen = open(file, "r")
    filetext = fileopen.read()
    fileopen.close()

    moduleblocks = re.findall(r"module +[\w|\W]+?endmodule *: *\w+", filetext)

    if moduleblocks != []:
        for moduleblock in moduleblocks:

            modulename = re.search(r"endmodule *: *(\w+)", moduleblock)[1]

            inouts = []  # список всех input/output/inout индентификаторов

            # поиск всех input/output/inout индентификаторов
            inouts_strs = re.findall(r"(?:input|output|inout) +([\w|\W]*?[,;\n)=])", moduleblock)

            # выделение самих индентификаторов из списка inouts_strs
            for i in range(len(inouts_strs)):
                inouts += re.findall(r"(\w+) *[,;\n)=]", inouts_strs[i])

                # выделение индентификаторов, у которпых в конце [\d:\d]
                inouts += re.findall(r"(\w+) +\[[\d :]+][,;\n]", inouts_strs[i])

            modules[modulename] = inouts