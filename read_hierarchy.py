# — –»ѕ“ „“≈Ќ»я »≈–ј–’»» ѕ–ќ≈ “ј
# настройка конфигурации осуществл€етс€ в "read_hierarchy.json"

import json
import os
import re
from queue import Queue
import obfuscator
import work_with_files

# ------------------------------»Ќ»÷»јЋ»«ј÷»я_√ЋќЅјЋ№Ќџ’_ѕ≈–≈ћ≈ЌЌџ’------------------------------ #

json_file = open(r"jsons/read_hierarchy.json", "r")
json_struct = json.load(json_file)  # json словарь

files = work_with_files.get_sv_files(os.curdir)  # sv файлы всего проекта

# ifdef/ifndef обработка всех фалйов
for file_g in files:
    obfuscator.preobfuscator_ifdef(file_g)

modules = work_with_files.get_all_modules(os.curdir)  # все модули


# ------------------------------«јѕ”— _„“≈Ќ»я_»≈–ј–’»»------------------------------ #

# запуск чтени€ иерархии
def launch():
    # восстановление структуры вызовов модулей
    if json_struct["tasks"]["a"]:
        restoring_call_structure()

    # поиск иерархических путей ко всем обьектам модулей
    if json_struct["tasks"]["b"]:
        search_allmodule_objects()

    # разделение файлов с несколькими модул€ми
    if json_struct["tasks"]["c"]:
        splitting_modules_by_files()


# ------------------------------ќ—Ќќ¬Ќџ≈_‘”Ќ ÷»»------------------------------ #

# ф-€ запуска восстановлени€ структуры вызовов модулей
def restoring_call_structure():
    inst_in_modules_dict = get_insts_in_modules()  # словарь модулей (ключ - название модул€,
    # значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))

    # запись в файл отчета структуры вызовов модулей
    project_struct_report(json_struct["report_filename"], inst_in_modules_dict)

    # запись в файл отчета иерархических путей всех instance обьектов
    project_objects_inst_report(json_struct["report_filename"], inst_in_modules_dict)


# ф-€ запуска поиска иерархических путей ко всем обьектам модулей (reg, net, instance, port)
def search_allmodule_objects():

    inst_in_modules_dict = get_insts_in_modules()  # словарь модулей (ключ - название модул€,
    # значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))

    # поиск иерархических путей ко всем обьектам модулей (reg, net, instance, port)
    project_allobjects_report(json_struct["report_filename"], inst_in_modules_dict)


# ф-€ разделение файлов с несколькими модул€ми
def splitting_modules_by_files():

    # цикл по всем файлам
    for file in files:

        filetext = work_with_files.get_file_text(file)  # текст файла

        # список полных текстов блоков модулей файла
        moduleblocks = re.findall(r"module +[\w|\W]+?endmodule", filetext)

        # если нашли файл с более чем 1 модулем, то раздел€ем файл
        if len(moduleblocks) > 1:

            # цикл обработки каждого модул€ в файле
            for moduleblock in moduleblocks:

                modulename = re.search(r"module +(\w+)", moduleblock)[1]  # им€ модул€

                filetext_with_cur_module = filetext  # текст файла с текущим модулем

                # цикл удалени€ из текста файла других модулей
                for moduleblock_another in moduleblocks:
                    if moduleblock_another == moduleblock:
                        continue
                    else:
                        filetext_with_cur_module = filetext_with_cur_module.replace(moduleblock_another, '')

                # саздаем новый файл с отдельным модулем и вписываем туда основной код файла и текст модул€
                work_with_files.write_text_to_file(re.sub(r"[\w\.]+$", modulename, file) + ".sv",
                                                   filetext_with_cur_module)

            # удал€ем файл с несколькими модул€ми
            os.remove(file)


# ------------------------------‘”Ќ ÷»»_ѕ»— ј_»_ѕ≈„ј“»_»≈–ј–’»»------------------------------ #

# ф-€ поиска корневых модулей
def get_roots_modules(inst_in_modules_dict):
    roots = []  # корневые модули

    insts = get_inst_list(inst_in_modules_dict)  # список всех instance обьектов

    # цикл проверик каждого модул€ на то €вл€етс€ ли он корневым
    for module in inst_in_modules_dict:

        # если список instance обьектов модул€ не пуст - то провер€ем его
        if inst_in_modules_dict[module]:

            # флаг - нет ли на instance обьект ссылки, т.е. этот модуль не имеет нигле экземпл€ров,
            # т.е. это флаг корневого модул€
            no_link_flag = True

            # проходимс€ по всем instance обьектам, чтобы найти хот€ бы 1 ссылку на модуль
            for inst in insts:

                # ссылка на обьект есть, если текущий обьект имеет тип модул€ module
                if re.search(r"\((\w+)\)", inst)[1] == module:
                    no_link_flag = False

            # если флаг был изменен, то добавл€ем корневой модуль
            if no_link_flag:
                roots.append(module)

    return roots


# ф-€ чтени€ струкутры вызовов модулей проекта и записи соответствующего отчета в файл
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

        # добавление instance обьектов в корневых модул€х в очередь
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(inst)

    # цикл печати instance обьектов в отчет (что-то типо поиска в ширину)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # текущий модуль, вз€тый из очереди

        # печать списка instance обьектов текущего модул€
        fileopen.write(cur_module + " -> " + str(
            inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]) + "\n\n")

        # цикл добавлени€ instance обьектов текущего модул€ в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

    fileopen.close()  # закрытие файла


# ф-€ поиска и печати в отчет иерархических путей ко всем instance обьектам
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

        # добавление instance обьектов в корневых модул€х в очередь
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root + '.' + inst)

    # цикл печати instance обьектов в отчет (что-то типо поиска в ширину)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # текущий instance обьект, вз€тый из очереди

        # печатаем текущий instance обьект (без типа в круглых скобках)
        fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "\n\n")

        # цикл добавлени€ instance обьектов текущего модул€ в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)

    fileopen.close()  # закрытие файла


# ф-€ поиска и печати иерархических путей всех обьектов (reg, net, instance, port)
def project_allobjects_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # открытие файла
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")

    # получаем список корневых модулей
    roots = get_roots_modules(inst_in_modules_dict)

    # получаем словарь модулей со всеми их обьектами (reg, net, instance, port)
    modules_with_objects = work_with_files.get_all_modules(os.curdir, False)

    modules_queue = Queue()  # очередь instance обьектов

    # печать корневых модулей
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # цикл печати обьектов (reg, net, instance, port) корневых модулей в отчет
    # и добавлени€ instance обьектов корневых модулей в очередь
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

        cur_module = modules_queue.get()  # текущий instance обьект, вз€тый из очереди

        # цикл печати иерархических путей всех обьектов (reg, net, instance, port) текущего instance обьекта
        for typeobject in modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]]:
            for i in range(len(modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject])):
                fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "." +
                               modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject][
                                   i] + " ( " + typeobject + " ) \n")

        # цикл добавлени€ instance обьектов текущего модул€ в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)

    fileopen.close()  # закрытие файла


# ------------------------------¬—ѕќћќ√ј“≈Ћ№Ќџ≈_‘”Ќ ÷»»------------------------------ #

# ф-€ получени€ списка всех instance обьектов по словарю модулей (в круглых скобках - тип обьекта)
def get_inst_list(insts_in_modules_dict):

    insts = []  # список instance обьектов

    # цикл добавлени€ instance обьектов из словар€ в список
    for module in insts_in_modules_dict:
        insts += insts_in_modules_dict[module]

    return insts


# ф-€ создани€ словар€ модулей (ключ - название модул€,
# значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))
def get_insts_in_modules():
    insts_in_modules_dict = {}  # словарь модулей

    # цикл порлучени€ instance обьектов каждого файла
    for file in files:

        filetext = work_with_files.get_file_text(file)  # текст файла

        # список полных текстов блоков модулей файла
        moduleblocks = re.findall(r"module +[\w|\W]+?endmodule", filetext)

        # цикл поиска instance обьектов во всех модул€х файла
        for moduleblock in moduleblocks:

            modulename = re.search(r"module +(\w+)", moduleblock)[1]  # им€ модул€

            insts_in_modules_dict[modulename] = []  # инициализируем список instance обьектов модул€

            # цикл поиска instance модул€ module из списка modules в файле
            for module in modules:

                # поиск
                searched_instance = re.findall(module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)
                searched_instance += re.findall(module + r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)

                # добавление в список с типом в круглых скобках
                if searched_instance:
                    for inst in searched_instance:
                        insts_in_modules_dict[modulename].append(inst + "(" + module + ")")

                # если instance обьектов нет - продолжаем поиск
                else:
                    continue

    return insts_in_modules_dict




