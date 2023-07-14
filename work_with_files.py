# ФУНКЦИИ РАБОТЫ С ФАЙЛАМИ

import os
import re
import obfuscator


# ------------------------------ФУНКЦИИ_РАБОТЫ_С_ТЕКСТОМ_ФАЙЛА------------------------------ #
# ф-я отдающая текст файла
def get_file_text(file):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    return filetext


# ф-я записи текста в файл
def write_text_to_file(file, text):

    fileopen = open(file, "w")
    fileopen.write(text)
    fileopen.close()


# добавление текста в файл
def add_text_to_file(text, file):

    fileopen = open(file, "a")
    fileopen.write(text + "\n")
    fileopen.close()


# ------------------------------ФУНКЦИИ_ПОИСКА_ФАЙЛОВ_SV------------------------------ #
# ф-я поиска всех sv файлов (путей у них) в директории и поддиректориях
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
def get_sv_files(dir):
    svfiles = []  # список путей sv файлов
    scan_svfiles(dir, svfiles)
    return svfiles


# ------------------------------ФУНКЦИИ_ПОИСКА_МОДУЛЕЙ------------------------------ #
# ф-я поиска списка всех модулей проекта или же словаря модулей (с обьектами reg, net, instance, port)
def get_all_modules(onlymodules = True):
    # onlymodules - флаг работы со списком или словарем
    # перед поиском желательно удалить все комментарии и выполнить обработку ifdef/ifndef
    # можно использовать obfuscator.preobfuscator()

    svfiles = get_sv_files(os.curdir)  # список путей sv файлов

    # если флаг onlymodules = false то работаем со словарем
    if not onlymodules:

        modules = {}  # словарь модулей во всем проекте, где ключ - название модуля,
        # а значение - словарь типов reg, net, instance, port со списками соответствующих обьектов

    # если флаг onlymodules = true то работаем со списком
    else:
        modules = []  # список модулей во всем проекте

    # поиск модулей во всех файлах
    for svfile in svfiles:
        filetext = get_file_text(svfile)
        if not onlymodules:
            modules.update(get_modules(filetext, onlymodules))
        else:
            modules += get_modules(filetext, onlymodules)

    return modules


# ф-я поиска либо словаря модулей либо списка модулей в 1 файле
def get_modules(text, onlymodules=True):

    # если флаг onlymodules = false то работаем со словарем
    if not onlymodules:

        modules = {}  # словарь модулей во всем проекте, где ключ - название модуля,
        # а значение - словарь типов reg, net, instance, port со списками соответствующих обьектов

    # если флаг onlymodules = true то работаем со списком
    else:
        modules = []  # список модулей во всем проекте

    # список полных текстов блоков модулей файла
    moduleblocks = get_module_blocks(text)

    # цикл обработки всех модулей
    for moduleblock in moduleblocks:

        modulename = re.search(r"module +(\w+)", moduleblock)[1]  # имя модуля

        # если обрабатываем словарь модулей
        if not onlymodules:

            inouts = obfuscator.search_inouts(moduleblock)  # список портов модуля

            instances = obfuscator.search_instances(moduleblock)  # список instance обьектов модуля

            nets_strs = re.findall(
                r"(?:wire|tri|tri0|tri1|supply0|"  # список строк обьектами nets
                r"supply1|trireg|wor|triand|"
                r"trior|wand) +([\w :\[\]\-`]*?[,;\n)=])", moduleblock)

            nets_strs += re.findall(r"(?:wire|tri|tri0|tri1|supply0|"  # список строк с структурами обьектов nets
                                    r"supply1|trireg|wor|triand|"
                                    r"trior|wand) +struct[\w :\[\]\-`]*?\{[\w|\W]*?} *(\w+)[,;\n)=]", moduleblock)

            nets = []  # итоговый список с nets обьектами

            # выделение самих идентификаторов из списка nets
            for i in range(len(nets_strs)):
                nets += re.findall(r"(\w+) *[,;\n)=]", nets_strs[i])

                # выделение идентификаторов, у которых в конце [\d:\d]
                nets += re.findall(r"(\w+) +\[[\d :\-*\w`]+] *[,;=\n]", nets_strs[i])

            regs = obfuscator.base_ind_search(moduleblock, ["reg"])

            allind = set(inouts + regs + nets + instances)  # список всех идентификаторов

            # удаление из списка allind найденных input/output/inout идентификаторов
            obfuscator.delete_inouts(inouts, allind)

            # добавление обьектов reg, net, instance, port в словарь
            modules[modulename] = {}
            modules[modulename]["port"] = inouts
            modules[modulename]["net"] = nets
            modules[modulename]["regs"] = regs
            modules[modulename]["instances"] = instances

        # если обрабатываем список модулей
        else:

            # добавляем модуль в список
            modules.append(modulename)

    return modules


# ф-я возвращающая блоки текста модулей или текст конкретного модуля
def get_module_blocks(text, modulename = None):

    if modulename:
        module_block = re.search(r"\Wmodule +" + modulename + r"[\w|\W]+?endmodule", text)
        if module_block:
            return module_block[0]
        else:
            return []
    else:
        return re.findall(r"\Wmodule +[\w|\W]+?endmodule", text)