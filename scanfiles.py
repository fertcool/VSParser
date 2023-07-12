import os
import re
import obfuscator


# ф-я поиска всех sv файлов (путей у ним) в директории и поддиректориях
def scan_svfiles(dir, svfiles):
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
        scan_svfiles(dir + "\\" + path, svfiles)


# ф-я получить список sv файлов
def getsv(dir):
    svfiles = []  # список путей sv файлов
    scan_svfiles(dir, svfiles)
    return svfiles


# ф-я поиска списка всех модулей проекта или же словаря модулей (с обьектами reg, net, instance, port)
def getallmodules(dir, onlymodules = True):

    # перед поиском желательно удалить все комментарии и выполнить обработку ifdef/ifndef
    # можно использовать obfuscator.preobfuscator()

    svfiles = getsv(dir)  # список путей sv файлов
    # если флаг onlymodules = false то работаем со словарем
    if not onlymodules:

        modules = {}  # словарь модулей во всем проекте, где ключ - название модуля,
        # а значение - словарь типов reg, net, instance, port со списками соответствующих обьектов

    # если флаг onlymodules = true то работаем со списком
    else:
        modules = []  # список модулей во всем проекте

    # поиск модулей во всех файлах
    for svfile in svfiles:
        getmodules_infile(svfile, modules, onlymodules)

    return modules


# ф-я поиска либо словаря модулей либо списка модулей в 1 файле
def getmodules_infile(file, modules, onlymodules=True):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    # список полных текстов блоков модулей файла
    moduleblocks = re.findall(r"module +[\w|\W]+?endmodule", filetext)

    # цикл обработки всех модулей
    for moduleblock in moduleblocks:

        modulename = re.search(r"module +(\w+)", moduleblock)[1]  # имя модуля

        # если обрабатываем словарь модулей
        if not onlymodules:

            # записываем в файл только текст модуля
            fileopenwm = open(file, "w")
            fileopenwm.write(moduleblock)
            fileopenwm.close()

            inouts = obfuscator.search_inouts(moduleblock)  # список портов модуля

            instances = obfuscator.search_instances(file)  # список instance обьектов модуля

            regs_strs = re.findall(r"reg +([\w :\[\]\-`]*?[,;\n)=])", moduleblock)  # список строк с обьектами regs

            nets_strs = re.findall(
                r"(?:wire|tri|tri0|tri1|supply0|"  # список строк обьектами nets
                r"supply1|trireg|wor|triand|"
                r"trior|wand) +([\w :\[\]\-`]*?[,;\n)=])", moduleblock)
            nets_strs += re.findall(r"(?:wire|tri|tri0|tri1|supply0|"  # список строк с структурами обьектов nets
                                    r"supply1|trireg|wor|triand|"
                                    r"trior|wand) +struct[\w :\[\]\-`]*?\{[\w|\W]*?} *(\w+)[,;\n)=]", moduleblock)
            nets = []
            # выделение самих индентификаторов из списка nets
            for i in range(len(nets_strs)):
                nets += re.findall(r"(\w+) *[,;\n)=]", nets_strs[i])

                # выделение индентификаторов, у которпых в конце [\d:\d]
                nets += re.findall(r"(\w+) +[\d :\[\]]+[,;\n]", nets_strs[i])
            regs = []
            # выделение самих индентификаторов из списка nets
            for i in range(len(regs_strs)):
                regs += re.findall(r"(\w+) *[,;\n)=]", regs_strs[i])

                # выделение индентификаторов, у которпых в конце [\d:\d]
                regs += re.findall(r"(\w+) +\[[\d :]+][,;\n]", regs_strs[i])

            allind = inouts + regs + nets + instances  # список всех идентификаторов

            # удаление из списка allind найденных input/output/inout индентификаторов
            for i in range(len(inouts)):
                if inouts[i] in allind:
                    allind.remove(inouts[i])

            # добавление обьектов reg, net, instance, port в словарь
            modules[modulename] = {}
            modules[modulename]["port"] = inouts
            modules[modulename]["net"] = nets
            modules[modulename]["regs"] = regs
            modules[modulename]["instances"] = instances

            # обратно записываем код в файл
            fileopenwm = open(file, "w")
            fileopenwm.write(filetext)
            fileopenwm.close()

        # если обрабатываем список модулей
        else:

            # добавляем модуль в список
            modules.append(modulename)
