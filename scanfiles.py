import os
import re

import obfuscator


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


def getallmodules(dir, onlymodules = True):

    # перед поиском желательно удалить все комментарии и выполнить обработку ifdef/ifndef
    # можно использовать obfuscator.preobfuscator()

    svfiles = getsv(dir)  # список путей sv файлов
    if not onlymodules:
        modules = {}  # словарь модулей во всем проекте, где ключ - название модуля, а значение - список его портов
    else:
        modules = []
    for svfile in svfiles:
        getmodules_infile(svfile, modules, onlymodules)

    return modules


def getmodules_infile(file, modules, onlymodules = True):
    fileopen = open(file, "r")
    filetext = fileopen.read()
    fileopen.close()

    moduleblocks = re.findall(r"module +[\w|\W]+?endmodule *: *\w+", filetext)

    if moduleblocks:
        for moduleblock in moduleblocks:

            modulename = re.search(r"endmodule *: *(\w+)", moduleblock)[1]

            if not onlymodules:
                fileopenwm = open(file, "w")
                fileopenwm.write(moduleblock)
                fileopenwm.close()

                inouts = obfuscator.search_inouts(moduleblock)
                instances = obfuscator.search_instances(file)
                regs_strs = re.findall(r"reg +([\w|\W]*?[,;\n)=])", moduleblock)
                nets_strs = re.findall(
        r"(?:wire|tri|tri0|tri1|supply0|"  # список строк с информацией после типа индентификатора
        r"supply1|trireg|wor|triand|"
        r"trior|wand) +([\w|\W]*?[,;\n)=])", moduleblock)
                nets = []
                # выделение самих индентификаторов из списка nets
                for i in range(len(nets_strs)):
                    nets += re.findall(r"(\w+) *[,;\n)=]", nets_strs[i])

                    # выделение индентификаторов, у которпых в конце [\d:\d]
                    nets += re.findall(r"(\w+) +\[[\d :]+][,;\n]", nets_strs[i])
                regs = []
                # выделение самих индентификаторов из списка nets
                for i in range(len(regs_strs)):
                    regs += re.findall(r"(\w+) *[,;\n)=]", regs_strs[i])

                    # выделение индентификаторов, у которпых в конце [\d:\d]
                    regs += re.findall(r"(\w+) +\[[\d :]+][,;\n]", regs_strs[i])

                allind = inouts+regs+nets+instances
                # удаление из списка allind найденных input/output/inout индентификаторов
                for i in range(len(inouts)):
                    if inouts[i] in allind:
                        allind.remove(inouts[i])




                modules[modulename] = {}
                modules[modulename]["port"] = inouts
                modules[modulename]["net"] = nets
                modules[modulename]["regs"] = regs
                modules[modulename]["instances"] = instances

                fileopenwm = open(file, "w")
                fileopenwm.write(filetext)
                fileopenwm.close()
            else:
                modules.append(modulename)