# СКРИПТ ОБФУСКАЦИИ ФАЙЛОВ
# настройка конфигурации осуществляется в "obfuscator.json"

# обфускация производится над идентификаторами:
# input / output / inout
# wire / reg
# module / function / task
# instance
# parameter / localparam
# byte / shortint / int / integer / longint / integer / bit / logic / shortreal / real
# realtime / time
# event
# enum / typedef
# `define
# обфускация не производится над вызовами instance обьектов через "."


import json
import os
import random
import re
import string
import erase_comments
import ifdefprocessing
import work_with_files


# ------------------------------ЗАПУСК_ОБФУСКАЦИИ------------------------------ #

def launch():
    json_file = open(r"jsons/obfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = work_with_files.get_sv_files(os.curdir)  # добавляем файлы всего проекта
    else:
        files.append(json_struct["conf"]["filename"])  # добавляем 1 необходимый файл

    # обфускация по всем идентификаторам
    if json_struct["tasks"]["a"]:

        # цикл по всем файлам
        for file in files:
            allind_search_and_replace(file)

    # обфускация по выбранному классу идентификаторов (input/output/inout, wire, reg, module, instance, parameter)
    if json_struct["tasks"]["b"]:

        # цикл по всем файлам
        for file in files:
            ind_search_and_replace(file, json_struct["literalclass"])

    # обфускация по идентификаторам input/output/inout в заданном модуле
    if json_struct["tasks"]["c"]:

        # цикл по всем файлам
        for file in files:
            module_search_and_replace_wo_inout(file, json_struct["module"])

    # обфускация в рамках (protect on - protect off)
    if json_struct["tasks"]["d"]:

        # цикл по всем файлам
        for file in files:
            ind_search_and_replace_protect(file)


# ------------------------------ОСНОВНЫЕ_ФУНКЦИИ------------------------------ #

# ф-я обфускации текста в пределах `pragma protect on - `pragma protect off
def ind_search_and_replace_protect(file):
    filetext = work_with_files.get_file_text(file)  # текст файла

    # текст обрабатываемого блока кода
    protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

    if protectblocks:
        # обработка ifdef/ifndef
        preobfuscator_ifdef(file)

        filetext = work_with_files.get_file_text(file)  # текст всего файла после обработки ifdef/ifndef

        # повторяем поиск, т.к. провели обработку ifdef/ifndef
        protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

        # цикл обработки блоков кода
        for protectblock in protectblocks:
            filetext = work_with_files.get_file_text(file)  # текст всего файла после обработки ifdef/ifndef

            # запись в файл текста protect блока
            work_with_files.write_text_to_file(file, protectblock)

            # заменяем все идентификаторы в protect блоке
            allind_search_and_replace(file)

            # чтение нового текста модуля из файла
            newprotectblock = work_with_files.get_file_text(file)

            # запись в файл текста с обработанным protect блоком
            work_with_files.write_text_to_file(file, filetext.replace("`pragma protect on" + protectblock
                                                                      + "`pragma protect off", newprotectblock))

    else:
        return


# ф-я поиска и замены любых идентификаторов, кроме input/output/inout в заданном модуле
def module_search_and_replace_wo_inout(file, module):
    filetext = work_with_files.get_file_text(file)  # текст файла

    moduleblock = re.search(r"\Wmodule +" + module + r"[\w|\W]+?endmodule", filetext)

    # если нашли модуль, то обрабатываем его
    if moduleblock:

        # обработка ifdef/ifndef
        preobfuscator_ifdef(file)

        moduletext = re.search(r"\Wmodule +" + module + r"[\w|\W]+?endmodule", filetext)[0]  # текст блока модуля

        # запись модуля в текст (на замену старому коду будет только обрабатываемый модуль)
        work_with_files.write_text_to_file(file, moduletext)

        # шифруем блоки instance, чтобы они не участвовали далее в обрвботке
        decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

        newmoduletext = work_with_files.get_file_text(file)  # текст модуля после шифровки instance обьектов

        # instance идентификаторы (имена)
        instances = search_instances(file)

        inouts = search_inouts(newmoduletext)  # список всех input/output/inout идентификаторов

        defines = re.findall(r"`define +(\w+)", newmoduletext)  # список идентификаторов define

        # список строк с определением или инициализацией базовых идентификаторов
        # в группе хранятся списки идентификаторов
        base = base_ind_search(newmoduletext, ["wire", "reg", "parameter", "localparam", "byte", "shortint",
                                               "int", "integer", "longint", "bit", "logic", "shortreal",
                                               "real", "realtime", "time", "event"])

        enums = enum_ind_search(newmoduletext)  # идентификаторы enums

        structs = re.findall(r"\Wstruct[\w|\W]+?} *(\w+);", newmoduletext)  # список идентификаторов struct

        typedefs = re.findall(r"\Wtypedef[\w|\W]+?} *(\w+);", newmoduletext)  # список идентификаторов typedef

        # удаление повторных идентификаторов typedef из enums и struct
        for a in structs:
            if a in typedefs:
                structs.remove(a)
        for a in enums:
            if a in typedefs:
                enums.remove(a)

        # поиск идентификаторов, типа typedef'ов
        for typedef in typedefs:
            base_typedef = re.findall(typedef + r" +(.*?[,;\n)=])", newmoduletext)
            for i in range(len(base_typedef)):
                base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # добавление найденных идентификаторов в base

        # поиск идентификаторов функций
        module_ind = re.findall(r"\W(?:function|task)[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", newmoduletext)

        # все идентификаторы (без повторов)
        allind = set(defines + base + enums + structs + typedefs + module_ind + instances)  # все идентификаторы

        # удаление из списка allind найденных input/output/inout идентификаторов
        delete_inouts(inouts, allind)

        # шифровка идентификаторов и создание таблицы соответствия
        decrypt_table = {}
        encrypt_file(allind, file, newmoduletext, decrypt_table)

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

        # проверяем есть ли в модуле параметры
        modules = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?#\(",
                             newmoduletext)  # список модулей, описанных в тексте файла
        # если нашли, то заменяем их в других файлах
        if modules:
            # заменяем все instance блоки в других файлах (именно параметры)
            change_instances_ports_allf(modules, inv_decrypt_table)

        # чтение нового текста модуля из файла
        newmoduletext = work_with_files.get_file_text(file)

        # дешифруем instance блоки
        for decr_inst in decrypt_table_instances:
            newmoduletext = newmoduletext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # заменяем идентификаторы instance
        for inst in instances:
            newmoduletext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", newmoduletext)

        # создаем файл с таблицей соответствия
        write_decrt_in_file(file, decrypt_table)

        # запись в файл текст с обработанным блоком module
        work_with_files.write_text_to_file(file, filetext.replace(moduletext, newmoduletext))
    else:
        print(module + " in " + file + " not found")
        return


# ф-я поиска и замены выбранного вида идентификаторов (input/output/inout, wire, reg, module, instance, parameter)
def ind_search_and_replace(file, ind):
    # обработка ifdef/ifndef
    preobfuscator_ifdef(file)

    # шифруем блоки instance, чтобы они не участвовали далее в обработке
    decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

    filetext = work_with_files.get_file_text(file)  # текст файла

    decrypt_table = {}  # таблица соответствия для замененных идентификаторов

    allind = []  # список всех идентификаторов

    # коррекция
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # если выбранный тип идентификатора - "базовый", то проводим соответствующий поиск
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        # поиск всех идентификаторов типа ind
        allind = base_ind_search(filetext, [ind])

        # обрабатываем не порты
        if ind != "(?:input|output|inout)":

            # обрабатываем parameter
            if ind == "parameter":

                # шифровка идентификаторов
                encrypt_file(allind, file, filetext, decrypt_table)

                # ищем модули с параметрами
                modules = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?#\(",
                                     filetext)  # список модулей, описанных в тексте файла
                # если нашли, то заменяем их в других файлах
                if modules:
                    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

                    # заменяем все instance блоки в других файлах (именно параметры)
                    change_instances_ports_allf(modules, inv_decrypt_table)

                # создаем файл с таблицей соответствия
                write_decrt_in_file(file, decrypt_table)

                filetext = work_with_files.get_file_text(file)  # текст файла

                # дешифруем instance блоки
                for decr_inst in decrypt_table_instances:
                    filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

                # запись обфусцированного текста
                work_with_files.write_text_to_file(file, filetext)

            # обрабатываем reg, wire
            else:
                inouts = search_inouts(filetext)

                # удаляем input/output/inout порты из allind
                delete_inouts(inouts, allind)

                # шифровка идентификаторов и создание таблицы соответствия
                encrypt_file(allind, file, filetext, decrypt_table)
                write_decrt_in_file(file, decrypt_table)

        # если обрабатываем input/output/inout порты, то надо в других файлах обработать порты instance
        # обьектов соответсвующих модулей
        else:
            # шифровка идентификаторов
            encrypt_file(allind, file, filetext, decrypt_table)

            inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

            modules = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()",
                                 filetext)  # список модулей, описанных в тексте файла

            # заменяем все instance блоки в других файлах, тк мы изменили названия портов функций modules
            change_instances_ports_allf(modules, inv_decrypt_table)

            filetext = work_with_files.get_file_text(file)  # текст файла

            # создаем файл с таблицей соответствия
            write_decrt_in_file(file, decrypt_table)

            # дешифруем instance блоки
            for decr_inst in decrypt_table_instances:
                filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

            # запись обфусцированного текста
            work_with_files.write_text_to_file(file, filetext)

    # если выбранный тип идентификатора module - то заменяем идентификаторы модулей и тип
    # instance обьектов в других файлах
    elif ind == "module":

        # поиск идентификаторов модулей
        allind = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

        # шифровка идентификаторов
        encrypt_file(allind, file, filetext, decrypt_table)

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

        # заменяем все типы instance блоков в других файлах
        change_instances_ports_allf(allind, inv_decrypt_table)

        # создаем файл с таблицей соответствия
        write_decrt_in_file(file, decrypt_table)

        filetext = work_with_files.get_file_text(file)  # текст файла

        # дешифруем instance блоки
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # запись обфусцированного текста
        work_with_files.write_text_to_file(file, filetext)

    # замена instance идентификаторов
    elif ind == "instance":

        # дешифруем instance блоки
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # запись текста после дешифрации
        work_with_files.write_text_to_file(file, filetext)

        # поиск всех instance идентификаторов
        allind = search_instances(file)

        # шифровка instance идентификаторов и создание таблицы соответствия
        encrypt_text(allind, "", decrypt_table)
        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия
        for inst in allind:
            filetext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", filetext)

        # запись обфусцированного текста
        work_with_files.write_text_to_file(file, filetext)

        write_decrt_in_file(file, decrypt_table)

    # ошибка
    else:
        print("literal not correct")
        return


# ф-я поиска и замены любых идентификаторов
def allind_search_and_replace(file):
    # обработка ifdef/ifndef
    preobfuscator_ifdef(file)

    # instance идентификаторы (имена)
    instances = search_instances(file)

    # шифруем блоки instance, чтобы они не участвовали далее в обрвботке
    decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

    filetext = work_with_files.get_file_text(file)  # текст файла после ifdef обработки и шифровки instance обьектов

    defines = re.findall(r"`define +(\w+)", filetext)  # список идентификаторов define

    # список строк с определением или инициализацией базовых идентификаторов
    # в группе хранятся списки идентификаторов
    base = base_ind_search(filetext, ["input", "output", "inout", "wire", "reg",
                                      "parameter", "localparam", "byte", "shortint",
                                      "int", "integer", "longint", "bit", "logic", "shortreal",
                                      "real", "realtime", "time", "event"])

    enums = enum_ind_search(filetext)  # список идентификаторов enums

    structs = re.findall(r"\Wstruct[\w|\W]+?} *(\w+);", filetext)  # список идентификаторов struct

    typedefs = re.findall(r"\Wtypedef[\w|\W]+?} *(\w+);", filetext)  # список идентификаторов typedef

    # удаление повторных идентификаторов typedef из enums и struct
    for a in structs:
        if a in typedefs:
            structs.remove(a)
    for a in enums:
        if a in typedefs:
            enums.remove(a)

    # поиск идентификаторов, типа typedef'ов
    for typedef in typedefs:
        base_typedef = re.findall(typedef + r" +(.*?[,;\n)=])", filetext)
        for i in range(len(base_typedef)):
            base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # добавление найденных идентификаторов в base

    # поиск идентификаторов модулей и функций
    ModuleClusses = re.findall(r"\W(?:module|task|function)[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    # все идентификаторы (без повторов)
    allind = set(defines + base + enums + structs + typedefs + ModuleClusses + instances)  # все идентификаторы

    # шифровка идентификаторов и создание таблицы соответствия
    decrypt_table = {}
    encrypt_file(allind, file, filetext, decrypt_table)

    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

    modules = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()",
                         filetext)  # список модулей, описанных в тексте файла

    # заменяем все instance блоки в других файлах, тк мы изменили названия портов функций modules
    change_instances_ports_allf(modules, inv_decrypt_table)

    filetext = work_with_files.get_file_text(file)  # текст файла после шифрации части идентификаторов

    # создаем файл с таблицей соответствия
    write_decrt_in_file(file, decrypt_table)

    # дешифруем instance блоки
    for decr_inst in decrypt_table_instances:
        filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

    # шифруем входные данные портов instance блока
    for invdt in inv_decrypt_table:
        ports = set(re.findall(r"\( *" + invdt + r"\W", filetext))
        for port in ports:
            # заменяем некоторые симвылы для правильной задачи регулярного выражения
            port = regexp_to_str(port)

            filetext = re.sub(port, "(" + inv_decrypt_table[re.search(r"\w+", port)[0]] + port[-1], filetext)

    # заменяем инлентификаторы instance
    for inst in instances:
        filetext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", filetext)

    # запись обфусцированного текста
    work_with_files.write_text_to_file(file, filetext)


# ф-я замены названий портов instance обьектов, их и типов во всех файлах проекта
def change_instances_ports_allf(modules, decr_table):
    files = work_with_files.get_sv_files(os.curdir)  # все файлы

    # цикл изменения портов во всех файлах
    for file in files:

        # обрабатываем ifdef/ifndef
        preobfuscator_ifdef(file)

        decrypt_table_instances = {}  # таблица соответствия портов instance обьекта

        filetext = work_with_files.get_file_text(file)  # текст файла

        # цикл обработки instance обьектов модулей modules
        for module in modules:

            # находим все instance обьекты (их текст)
            instances = re.findall(r"\W" + module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
            instances += re.findall(r"\W" + module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)

            # если такие обьекты существуют, то обрабатываем их
            if instances:

                # цикл обработки кажого обьекта instance
                for instance in instances:

                    # сохраняем старый текст обьекта
                    oldinstance = instance

                    # поиск всех портов обьекта
                    inouts = re.findall(r"\.(\w+)", instance)

                    # цикл замены названия портов на соответствующие в таблице decr_table
                    for inout in inouts:
                        if inout in decr_table:
                            instance = change_ind(instance, inout, decr_table[inout])

                            # добавляем в таблицу decrypt_table_instances соответствующую замену из decr_table
                            decrypt_table_instances[decr_table[inout]] = inout

                    # если необходимо - заменяем название модуля instance обьекта и добавляем в таблицу
                    # decrypt_table_instances
                    if module in decr_table:
                        instance = re.sub(module, decr_table[module], instance, 1)  # заменяем только 1 вхождение
                        decrypt_table_instances[decr_table[module]] = module

                    # заменяем текст на измененный
                    filetext = filetext.replace(oldinstance, instance)

            # если таких обьектов нет, то продолжаем поиск
            else:
                continue
        # если таблица decrypt_table_instances не пуста, то записываем ее в файл таблиц соответствия
        if decrypt_table_instances:
            write_decrt_in_file(file, decrypt_table_instances)

        # запись измененного текста в файл
        work_with_files.write_text_to_file(file, filetext)


# ------------------------------ФУНКЦИИ_ШИФРОВАНИЯ------------------------------ #

# ф-я шиврования идентификаторов в тексте
def encrypt_text(allind, filetext, decrypt_table):
    # цикл замены всех идентификаторов
    for ind in allind:
        randlength = random.randint(8, 32)  # выбор случайной длины строки
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, randlength))  # ссоздание случайной строки

        decrypt_table[rand_string] = ind  # добавляем в таблицу новое соответствие новому идентификатору

        filetext = change_ind(filetext, ind, rand_string)

    return filetext


# ф-я записи вместо текста "text" зашиврованного текста в файл "file"
def encrypt_file(allind, file, text, decrypt_table):
    filetext = work_with_files.get_file_text(file)  # текст файла

    # заменяем на зашифрованный текст
    filetext = filetext.replace(text, encrypt_text(allind, text, decrypt_table))

    # записываем его
    work_with_files.write_text_to_file(file, filetext)


# ф-я создания (или добавление в существующий файл) таблицы замены идентификаторов
def write_decrt_in_file(file, decrypt_table):
    if decrypt_table:
        work_with_files.add_text_to_file(str(decrypt_table), file.replace(".sv", "_decrypt_table.txt"))


# ф-я замены идентификаторов в тексте на новые
def change_ind(text, ind, newind):
    indefic = set(re.findall(r'\W' + ind + r'\W', text))  # поиск всех совпадений с текущим идентификатором
    # ищем именно совпадения с несловесными символами по
    # бокам
    # цикл замены каждого совпадения на случайную строку
    for indef in indefic:
        first = indef[0]  # несловесный символ слева от совпадения
        last = indef[-1]  # несловесный справа слева от совпадения

        # заменяем некоторые симвылы для правильной задачи регулярного выражения
        indef = regexp_to_str(indef)

        # замена совпадения на случайную строку
        text = re.sub(indef, first + newind + last, text)

    return text


# ф-я заменяющая регулярное выражение со спец. символами в обычную строку
def regexp_to_str(regexp):
    # заменяем некоторые симвылы для правильной задачи регулярного выражения
    regexp = regexp.replace("(", r"\(")
    regexp = regexp.replace("{", r"\{")
    regexp = regexp.replace(".", r"\.")
    regexp = regexp.replace("?", r"\?")
    regexp = regexp.replace("*", r"\*")
    regexp = regexp.replace("|", r"\|")
    regexp = regexp.replace("[", r"\[")
    regexp = regexp.replace(")", r"\)")
    regexp = regexp.replace("]", r"\]")
    regexp = regexp.replace("+", r"\+")

    return regexp


# ------------------------------ФУНКЦИИ_ПОИСКА_ИДЕНТИФИКАТОРОВ----------------------------- #

# возращает имена всех instance обьектов
def search_instances(file):
    filetext = work_with_files.get_file_text(file)  # текст файла

    # все модули и их порты
    modules = work_with_files.get_all_modules(os.curdir)

    instances = []  # список instance обьектов

    # цикл поиска instance модуля module из списка modules в файле
    for module in modules:

        # поиск
        searched_instance = re.findall(r"\W" + module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)
        searched_instance += re.findall(r"\W" + module + r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)

        # добавление в список
        if searched_instance:
            instances += searched_instance
        else:
            continue

    # возврат списка имен instance
    return instances


# ф-я поиска портов input/output/inout в тексте
def search_inouts(text):
    inouts = base_ind_search(text, ["(?:input|output|inout)"])  # список input/output/inout портов

    return inouts


# ф-я возвращающая список обычных строчных (без структур) идентификаторов в тексте
def base_ind_search(text, ind_list):
    base_ind_pattern = ind_list[0]

    # начало регулярного выражения для нахождения хотябы одного из идентификаторов
    if len(ind_list) > 1:
        base_ind_pattern = "(?:"
        for ind in ind_list:
            base_ind_pattern += ind + "|"
        base_ind_pattern = base_ind_pattern[:-1]
        base_ind_pattern += ")"

    # список строк с определением или инициализацией базовых идентификаторов
    # в группе хранятся списки идентификаторов
    base = []
    # список строк с информацией после типа идентификатора
    baseindentif = re.findall(r"\W" + base_ind_pattern + " +(.*?[,;)=])", text)

    # поиск строк со множественным определением
    baseindentif += re.findall(r"\W" + base_ind_pattern + " +.*?,(.*?;)", text)

    # поиск строк с \n в конце
    baseindentif += re.findall(r"\W" + base_ind_pattern + " +([^;,)=\n]+?\n)", text)

    # выделение самих идентификаторов из списка baseindentif
    for i in range(len(baseindentif)):
        base += re.findall(r"(\w+) *[,;)=\n]", baseindentif[i])

        # выделение идентификаторов, у которпых в конце [\d:\d]
        base += re.findall(r"(\w+) +\[[\d :\-*\w`]+] *[,;=\n]", baseindentif[i])

    return base


# ф-я возвращающая список идентификаторов, связанных с enum
def enum_ind_search(text):
    enums = []  # список идентифиакторов внутри блока enums и самих идентификатров определяемых enums

    # список строк с блоками enums
    # в 1 группе хранится текст внутри блока
    # во 2 группе хранятся идентификаторы enums
    enumblocks = re.findall(r"\Wenum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", text)

    # цикл обработки enums (выделения идентификаторов из текстов enums)
    for i in range(len(enumblocks)):
        insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # текст внтури блока без присваиваний
        insideind = re.findall(r"(\w+) *", insideWOeq)  # список идентификаторов внутри блока
        outsideind = re.findall(r"(\w+) *",
                                enumblocks[i][1])  # список идентификаторов снаружи блока (объекты enum)
        enumblocks[i] = (insideind + outsideind)
        enums += enumblocks[i]  # в итоге делаем список всех идентификаторов связанных с блоками enum

    return enums


# ------------------------------ВСПОМОГАТЕЛЬНЫЕ_ФУНКЦИИ----------------------------- #

# ф-я удаления из списка allind найденных input/output/inout идентификаторов
def delete_inouts(inouts, allind):
    for i in range(len(inouts)):
        if inouts[i] in allind:
            allind.remove(inouts[i])


# ф-я обработки ifdef/ifndef и удаления комментариев
def preobfuscator_ifdef(file):
    # json ifdef скрипта
    # нужен для включения доп. списка include
    json_file_ifdef = open("jsons/ifdefprocessing.json", "r")
    json_ifdef_struct = json.load(json_file_ifdef)

    # включаем все include файлы
    ifdefprocessing.include_for_file(file, json_ifdef_struct)
    # обрабатываем ifdef/ifndef
    ifdefprocessing.ifdef_pr_forfile(file, json_ifdef_struct)

    #  удаляем комментарии
    erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

    # добавляем в начало \n (нужно для правильного поиска идентификаторов)
    filetext = work_with_files.get_file_text(file)
    if filetext[0] != "\n":
        work_with_files.write_text_to_file(file, "\n" + filetext)


# ф-я скрывающая (замена на случайную строку) instance блоков, для правильной обработки остального текста
def preobfuscator_instance(file):
    filetext = work_with_files.get_file_text(file)  # текст файла

    modules = work_with_files.get_all_modules(os.curdir)  # все модули проекта

    decrypt_table = {}  # таблица соответствия зашифрованных блоков instance

    # цикл поиска и шиврования блоков instance
    for module in modules:

        # поиск
        searched_instances = re.findall(r"\W" + module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
        searched_instances += re.findall(r"\W" + module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)

        # если нашли, то заменяем все блоки
        if searched_instances:

            # замена блоков
            for instance_block in searched_instances:
                letters_and_digits = string.ascii_letters + string.digits
                rand_string = ''.join(random.sample(letters_and_digits, 40))  # создание случайной строки

                # сохраняем замену в таблице соответствия
                decrypt_table[rand_string] = instance_block

                # замена в тексте
                filetext = filetext.replace(instance_block, rand_string)

        # если не нашли, то продолжаем поиск
        else:
            continue

    # запись зашиврованного текста
    work_with_files.write_text_to_file(file, filetext)

    # возврат таблицы соответсвия зашиврованный блоков instance
    return decrypt_table

