# СКРИПТ ЧТЕНИЯ ИЕРАРХИИ ПРОЕКТА
# настройка конфигурации осуществляется в "read_hierarchy.json"

import json
import os
import re
from queue import Queue
import obfuscator
import work_with_files

# ------------------------------ИНИЦИАЛИЗАЦИЯ_ГЛОБАЛЬНЫХ_ПЕРЕМЕННЫХ------------------------------ #

json_file = open(r"jsons/read_hierarchy.json", "r")
json_struct = json.load(json_file)  # json словарь

files = work_with_files.get_sv_files(os.curdir)  # sv файлы всего проекта

# ifdef/ifndef обработка всех фалйов
for file_g in files:
    obfuscator.preobfuscator_ifdef(file_g)

modules = work_with_files.get_all_modules()  # все модули


# ------------------------------ЗАПУСК_ЧТЕНИЯ_ИЕРАРХИИ------------------------------ #

# запуск чтения иерархии
def launch():
    # восстановление структуры вызовов модулей
    if json_struct["tasks"]["a"]:
        restoring_call_structure()

    # поиск иерархических путей ко всем обьектам модулей
    if json_struct["tasks"]["b"]:
        search_allmodule_objects()

    # разделение файлов с несколькими модулями
    if json_struct["tasks"]["c"]:
        splitting_modules_by_files()


# ------------------------------ОСНОВНЫЕ_ФУНКЦИИ------------------------------ #

# ф-я запуска восстановления структуры вызовов модулей
def restoring_call_structure():
    inst_in_modules_dict = get_insts_in_modules()  # словарь модулей (ключ - название модуля,
    # значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))

    # запись в файл отчета структуры вызовов модулей
    project_struct_report(json_struct["report_filename"], inst_in_modules_dict)

    # запись в файл отчета иерархических путей всех instance обьектов
    project_objects_inst_report(json_struct["report_filename"], inst_in_modules_dict)


# ф-я запуска поиска иерархических путей ко всем обьектам модулей (reg, net, instance, port)
def search_allmodule_objects():

    inst_in_modules_dict = get_insts_in_modules()  # словарь модулей (ключ - название модуля,
    # значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))

    # поиск иерархических путей ко всем обьектам модулей (reg, net, instance, port)
    project_allobjects_report(json_struct["report_filename"], inst_in_modules_dict)


# ф-я разделение файлов с несколькими модулями
def splitting_modules_by_files():

    # цикл по всем файлам
    for file in files:

        filetext = work_with_files.get_file_text(file)  # текст файла

        # список полных текстов блоков модулей файла
        moduleblocks = work_with_files.get_module_blocks(filetext)

        # если нашли файл с более чем 1 модулем, то разделяем файл
        if len(moduleblocks) > 1:

            # цикл обработки каждого модуля в файле
            for moduleblock in moduleblocks:

                modulename = re.search(r"module +(\w+)", moduleblock)[1]  # имя модуля

                filetext_with_cur_module = filetext  # текст файла с текущим модулем

                # цикл удаления из текста файла других модулей
                for moduleblock_another in moduleblocks:
                    if moduleblock_another == moduleblock:
                        continue
                    else:
                        filetext_with_cur_module = filetext_with_cur_module.replace(moduleblock_another, '')

                # саздаем новый файл с отдельным модулем и вписываем туда основной код файла и текст модуля
                work_with_files.write_text_to_file(re.sub(r"[\w\.]+$", modulename, file) + ".sv",
                                                   filetext_with_cur_module)

            # удаляем файл с несколькими модулями
            os.remove(file)


# ------------------------------ФУНКЦИИ_ПИСКА_И_ПЕЧАТИ_ИЕРАРХИИ------------------------------ #

# ф-я поиска корневых модулей
def get_roots_modules(inst_in_modules_dict):
    roots = []  # корневые модули

    insts = get_inst_list(inst_in_modules_dict)  # список всех instance обьектов

    # цикл проверик каждого модуля на то является ли он корневым
    for module in inst_in_modules_dict:

        # если список instance обьектов модуля не пуст - то проверяем его
        if inst_in_modules_dict[module]:

            # флаг - нет ли на instance обьект ссылки, т.е. этот модуль не имеет нигле экземпляров,
            # т.е. это флаг корневого модуля
            no_link_flag = True

            # проходимся по всем instance обьектам, чтобы найти хотя бы 1 ссылку на модуль
            for inst in insts:

                # ссылка на обьект есть, если текущий обьект имеет тип модуля module
                if re.search(r"\((\w+)\)", inst)[1] == module:
                    no_link_flag = False

            # если флаг был изменен, то добавляем корневой модуль
            if no_link_flag:
                roots.append(module)

    return roots


# ф-я чтения струкутры вызовов модулей проекта и записи соответствующего отчета в файл
def project_struct_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # открытие файла

    fileopen.write("\n\n*------------------------------PROJECT_CALL_STRUCTURE------------------------------*\n")

    # получаем список корневых модулей
    roots = get_roots_modules(inst_in_modules_dict)

    # получаем список всех instance обьектов
    insts = get_inst_list(inst_in_modules_dict)

    used = {}  # словарь добавленных в отчет instance обьектов (чтобы не было повторных записей)
    for inst in insts:
        used[inst] = False

    modules_queue = Queue()  # очередь instance обьектов

    # печать корневых модулей
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # печать instance обьектов корневых модулей
    for root in roots:
        fileopen.write("ROOT: " + root + " -> " + str(inst_in_modules_dict[root]) + "\n\n")

        # добавление instance обьектов в корневых модулях в очередь
        for inst in inst_in_modules_dict[root]:
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

    # цикл печати instance обьектов в отчет (что-то типо поиска в ширину)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # текущий модуль, взятый из очереди

        # печать списка instance обьектов текущего модуля
        fileopen.write(cur_module + " -> " + str(
            inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]) + "\n\n")

        # цикл добавления instance обьектов текущего модуля в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

    fileopen.close()  # закрытие файла


# ф-я поиска и печати в отчет иерархических путей ко всем instance обьектам
def project_objects_inst_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # открытие файла
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")

    # получаем список корневых модулей
    roots = get_roots_modules(inst_in_modules_dict)

    modules_queue = Queue()  # очередь instance обьектов

    # печать корневых модулей
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # печать instance обьектов корневых модулей
    for root in roots:
        fileopen.write("ROOT: " + root + "\n\n")

        # добавление instance обьектов в корневых модулях в очередь
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root + '.' + inst)

    # цикл печати instance обьектов в отчет (что-то типо поиска в ширину)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # текущий instance обьект, взятый из очереди

        # печатаем текущий instance обьект (без типа в круглых скобках)
        fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "\n\n")

        # цикл добавления instance обьектов текущего модуля в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)

    fileopen.close()  # закрытие файла


# ф-я поиска и печати иерархических путей всех обьектов (reg, net, instance, port)
def project_allobjects_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # открытие файла
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")

    # получаем список корневых модулей
    roots = get_roots_modules(inst_in_modules_dict)

    # получаем словарь модулей со всеми их обьектами (reg, net, instance, port)
    modules_with_objects = work_with_files.get_all_modules(False)

    modules_queue = Queue()  # очередь instance обьектов

    # печать корневых модулей
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # цикл печати обьектов (reg, net, instance, port) корневых модулей в отчет
    # и добавления instance обьектов корневых модулей в очередь
    for root in roots:

        # цикл по всем типам (reg, net, instance, port)
        for typeobject in modules_with_objects[root]:
            # цикл по всем обьектам конкретного типа
            for i in range(len(modules_with_objects[root][typeobject])):
                fileopen.write(root + "." + modules_with_objects[root][typeobject][i] + " ( " + typeobject + " ) \n")

        # добавление instance обьектов корневых модулей в очередь
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root + '.' + inst)

    # цикл печати иерархических путей всех обьектов (reg, net, instance, port)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # текущий instance обьект, взятый из очереди

        # цикл печати иерархических путей всех обьектов (reg, net, instance, port) текущего instance обьекта
        for typeobject in modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]]:
            for i in range(len(modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject])):
                fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "." +
                               modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject][
                                   i] + " ( " + typeobject + " ) \n")

        # цикл добавления instance обьектов текущего модуля в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)

    fileopen.close()  # закрытие файла


# ------------------------------ВСПОМОГАТЕЛЬНЫЕ_ФУНКЦИИ------------------------------ #

# ф-я получения списка всех instance обьектов по словарю модулей (в круглых скобках - тип обьекта)
def get_inst_list(insts_in_modules_dict):

    insts = []  # список instance обьектов

    # цикл добавления instance обьектов из словаря в список
    for module in insts_in_modules_dict:
        insts += insts_in_modules_dict[module]

    return insts


# ф-я создания словаря модулей (ключ - название модуля,
# значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))
def get_insts_in_modules():
    insts_in_modules_dict = {}  # словарь модулей

    # цикл порлучения instance обьектов каждого файла
    for file in files:

        filetext = work_with_files.get_file_text(file)  # текст файла

        # список полных текстов блоков модулей файла
        moduleblocks = work_with_files.get_module_blocks(filetext)

        # цикл поиска instance обьектов во всех модулях файла
        for moduleblock in moduleblocks:

            modulename = re.search(r"module +(\w+)", moduleblock)[1]  # имя модуля

            insts_in_modules_dict[modulename] = []  # инициализируем список instance обьектов модуля

            # цикл поиска instance модуля module из списка modules в файле
            for module in modules:

                # поиск
                searched_instance = re.findall(r"(?<!module)[ \n]+" + module + r"[ \n]+(\w+)[ \n]*\([\w|\W]+?\) *;", moduleblock)
                searched_instance += re.findall(r"(?<!module)[ \n]+" + module + r"[ \n]+#\([\w|\W]+?\)[ \n]*(\w+)[ \n]*\([\w|\W]+?\) *;", moduleblock)

                # добавление в список с типом в круглых скобках
                if searched_instance:
                    for inst in searched_instance:
                        insts_in_modules_dict[modulename].append(inst + "(" + module + ")")

                # если instance обьектов нет - продолжаем поиск
                else:
                    continue

    return insts_in_modules_dict




