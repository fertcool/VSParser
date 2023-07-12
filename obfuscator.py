# обфускация производится над индентификаторами:
# input / output / inout
# wire / reg
# module / function / task
# instance (модуль внутри модуля)
# parameter / localparam
# byte / shortint / int / integer / longint / integer / bit / logic / shortreal / real
# realtime / time
# event
# enum / typedef
# `define

import ast
import json
import os
import random
import re
import string

import erase_comments
import ifdefprocessing
import scanfiles

# allmodules = scanfiles.getallmodules(os.curdir)  # все модули и их порты


# запуск обфускации
def launch():
    json_file = open(r"jsons/obfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.getsv(os.curdir)  # добавляем файлы всего проекта
    else:
        files.append(json_struct["conf"]["filename"])  # добавляем 1 необходимый файл

    # обфускация по всем индентификаторам
    if json_struct["tasks"]["a"]:

        # цикл по всем файлам
        for file in files:
            allind_search_and_replace(file)

    # обфускация по выбранному классу индентификаторов (input/output/inout, wire, reg, module, instance, parameter)
    if json_struct["tasks"]["b"]:

        # цикл по всем файлам
        for file in files:
            ind_search_and_replace(file, json_struct["literalclass"])

    # обфускация по индентификаторам input/output/inout в заданном модуле
    if json_struct["tasks"]["c"]:

        # цикл по всем файлам
        for file in files:
            module_search_and_replace_WOinout(file, json_struct["module"])

    # обфускация в рамках (protect on - protect off)
    if json_struct["tasks"]["d"]:

        # цикл по всем файлам
        for file in files:
            ind_search_and_replace_protect(file)


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

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст всего файла
    fileopen.close()

    fileopen = open(file, "w")  # открытие файла
    fileopen.write("\n"+filetext)
    fileopen.close()

def ind_search_and_replace_protect(file):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст всего файла
    fileopen.close()

    protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

    if protectblocks:
        # обработка ifdef/ifndef
        preobfuscator_ifdef(file)

        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст всего файла после обработки ifdef/ifndef
        fileopen.close()

        # повторяем поиск, т.к. провели обработку ifdef/ifndef
        protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

        for protectblock in protectblocks:
            fileopen = open(file, "r")  # открытие файла
            filetext = fileopen.read()  # текст всего файла после обработки ifdef/ifndef
            fileopen.close()

            # запись в файл текста protect блока
            fileopen = open(file, "w")  # открытие файла
            fileopen.write(protectblock)
            fileopen.close()

            # заменяем все индентификаторы в protect блоке
            allind_search_and_replace(file)

            # чтение нового текста модуля из файла
            fileopen = open(file, "r")  # открытие файла
            newprotectblock = fileopen.read()
            fileopen.close()

            # запись в файл текста с обработанным protect блоком
            fileopen = open(file, "w")  # открытие файла
            fileopen.write(filetext.replace("`pragma protect on" + protectblock + "`pragma protect off", newprotectblock))
            fileopen.close()
    else:
        return


# ф-я поиска и замены любых индентификаторов, кроме input/output/inout в заданном модуле
def module_search_and_replace_WOinout(file, module):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст всего файла
    fileopen.close()

    moduleblock = re.search(r"module +"+module+r"[\w|\W]+?endmodule", filetext)

    # если нашли модуль, то обрабатываем его
    if moduleblock:

        # обработка ifdef/ifndef
        preobfuscator_ifdef(file)

        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст всего файла после обработки ifdef/ifndef (до обработки модуля)
        fileopen.close()

        moduletext = re.search(r"module +"+module+r"[\w|\W]+?endmodule", filetext)[0]  # текст блока модуля

        # запись модуля в текст (на замену старому коду будет только обрабатываемый модуль)
        fileopen = open(file, "w")  # открытие файла
        fileopen.write(moduletext)
        fileopen.close()

        # instance индентификаторы (имена)
        instances = search_instances(file)

        inouts = search_inouts(moduletext)  # список всех input/output/inout индентификаторов

        defines = re.findall(r"`define +(\w+)", moduletext)  # список индентификаторов define

        # список строк с определением или инициализацией базовых индентификаторов
        # в группе хранятся списки индентификаторов
        base = []
        baseindentif = re.findall(
            "(?:wire|reg|"  # список строк с информацией после типа индентификатора
            "parameter|localparam|byte|shortint|"
            "int|integer|longint|bit|logic|shortreal|"
            "real|realtime|time|event"
            ") +([\w|\W]*?[,;\n)=])", moduletext)

        # выделение самих индентификаторов из списка baseindentif
        for i in range(len(baseindentif)):
            base += re.findall(r"(\w+) *[,;\n)=]", baseindentif[i])

            # выделение индентификаторов, у которпых в конце [\d:\d]
            base += re.findall(r"(\w+) +\[[\d :]+][,;\n]", baseindentif[i])

        # список строк с блоками enums
        # в 1 группе хранится текст внутри блока
        # во 2 группе хранятся индентификаторы enums
        enumblocks = re.findall(r"enum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", moduletext)
        enums = []  # список индентифиакторов внутри блока enums и самих индентификатров определяемых enums
        # цикл обработки enums (выделения индентификаторов из текстов enums)
        for i in range(len(enumblocks)):
            insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # текст внтури блока без присваиваний
            insideind = re.findall(r"(\w+) *", insideWOeq)  # список индентификаторов внутри блока
            outsideind = re.findall(r"(\w+) *",
                                    enumblocks[i][1])  # список индентификаторов снаружи блока (объекты enum)
            enumblocks[i] = (insideind + outsideind)
            enums += enumblocks[i]  # в итоге делаем список всех индентификаторов связанных с блоками enum

        structs = re.findall(r"struct[\w|\W]+?} *(\w+);", moduletext)  # список индентификаторов struct

        typedefs = re.findall(r"typedef[\w|\W]+?} *(\w+);", moduletext)  # список индентификаторов typedef

        # удаление повторных индентификаторов typedef из enums и struct
        for a in structs:
            if a in typedefs:
                structs.remove(a)
        for a in enums:
            if a in typedefs:
                enums.remove(a)

        # поиск индентификаторов, типа typedef'ов
        for typedef in typedefs:
            base_typedef = re.findall(typedef + r" +([\w|\W]*?[,;\n)=])", moduletext)
            for i in range(len(base_typedef)):
                base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # добавление найденных индентификаторов в base

        # поиск индентификаторов модулей и классов
        module_ind = re.findall(r"(?:function|task)[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", moduletext)

        # все индентификаторы (без повторов)
        allind = set(defines + base + enums + structs + typedefs + module_ind + instances)  # все индентификаторы

        # удаление из списка allind найденных input/output/inout индентификаторов
        for i in range(len(inouts)):
            if inouts[i] in allind:
                allind.remove(inouts[i])

        # шифровка индентификаторов и создание таблицы соответствия
        decrypt_table = {}
        encrypt_file(allind, file, moduletext, decrypt_table)

        # проверяем есть ли в модуле параметры
        modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?#\(",
                             moduletext)  # список модулей, описанных в тексте файла
        # если нашли, то заменяем их в других файлах
        if modules:
            inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

            # заменяем все instance блоки в других файлах (именно параметры)
            change_instances_ports_allf(modules, inv_decrypt_table)

        # создаем файл с таблицей соответствия
        write_decrt_in_file(file, decrypt_table)

        # чтение нового текста модуля из файла
        fileopen = open(file, "r")  # открытие файла
        newmoduletext = fileopen.read()
        fileopen.close()

        # запись в файл текст с обработанным блоком module
        fileopen = open(file, "w")  # открытие файла
        fileopen.write(filetext.replace(moduletext, newmoduletext))
        fileopen.close()
    else:
        print(module + " in " + file + " not found")
        return


# ф-я поиска и замены выбранного вида индентификаторов (input/output/inout, wire, reg, module, instance, parameter)
def ind_search_and_replace(file, ind):

    # обработка ifdef/ifndef
    preobfuscator_ifdef(file)

    # шифруем блоки instance, чтобы они не участвовали далее в обработке
    decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    decrypt_table = {}  # таблица соответствия для замененных индентификаторов

    allind = []  # список всех индентификаторов

    # коррекция
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # если выбранный тип индентификатора - "базовый", то проводим соответствующий поиск
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        # поиск всех идентификаторов типа ind (строк с ними)
        allinds_str = re.findall(ind + r" +([\w|\W]*?[,;\n)=])", filetext)

        # выделение самих индентификаторов из списка allinds_str
        for i in range(len(allinds_str)):
            allind += re.findall(r"(\w+) *[,;\n)=]", allinds_str[i])

            # выделение индентификаторов, у которпых в конце [\d:\d]
            allind += re.findall(r"(\w+) +\[[\d :]+][,;\n]", allinds_str[i])

        # обрабатываем не порты
        if ind != "(?:input|output|inout)":

            # обрабатываем parameter
            if ind == "parameter":

                # шифровка индентификаторов
                encrypt_file(allind, file, filetext, decrypt_table)

                # ищем модули с параметрами
                modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?#\(",
                                     filetext)  # список модулей, описанных в тексте файла
                # если нашли, то заменяем их в других файлах
                if modules:

                    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

                    # заменяем все instance блоки в других файлах (именно параметры)
                    change_instances_ports_allf(modules, inv_decrypt_table)

                # создаем файл с таблицей соответствия
                write_decrt_in_file(file, decrypt_table)

                fileopen = open(file, "r")  # открытие файла
                filetext = fileopen.read()  # текст файла
                fileopen.close()

                # дешифруем instance блоки
                for decr_inst in decrypt_table_instances:
                    filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

                # запись обфусцированного текста
                fileopen = open(file, "w")  # открытие файла
                fileopen.write(filetext)
                fileopen.close()

            # обрабатываем reg, wire
            else:
                inouts = search_inouts(filetext)

                # удаляем input/output/inout порты из allind
                for inout in inouts:
                    if inout in allind:
                        allind.remove(inout)

                # шифровка индентификаторов и создание таблицы соответствия
                encrypt_file(allind, file, filetext, decrypt_table)
                write_decrt_in_file(file, decrypt_table)

        # если обрабатываем input/output/inout порты, то надо в других файлах обработать порты instance
        # обьектов соответсвующих модулей
        else:
            # шифровка индентификаторов
            encrypt_file(allind, file, filetext, decrypt_table)

            inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

            modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()",
                                 filetext)  # список модулей, описанных в тексте файла

            # заменяем все instance блоки в других файлах, тк мы изменили названия портов функций modules
            change_instances_ports_allf(modules, inv_decrypt_table)

            fileopen = open(file, "r")  # открытие файла
            filetext = fileopen.read()  # текст файла
            fileopen.close()

            # создаем файл с таблицей соответствия
            write_decrt_in_file(file, decrypt_table)

            # дешифруем instance блоки
            for decr_inst in decrypt_table_instances:
                filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

            # запись обфусцированного текста
            fileopen = open(file, "w")  # открытие файла
            fileopen.write(filetext)
            fileopen.close()

    # если выбранный тип индентификатора module - то заменяем индентификаторы модулей и тип
    # instance обьектов в других файлах
    elif ind == "module":

        # поиск индентификаторов модулей
        allind = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

        # шифровка индентификаторов
        encrypt_file(allind, file, filetext, decrypt_table)

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

        # заменяем все типы instance блоков в других файлах
        change_instances_ports_allf(allind, inv_decrypt_table)

        # создаем файл с таблицей соответствия
        write_decrt_in_file(file, decrypt_table)

        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст файла
        fileopen.close()

        # дешифруем instance блоки
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # запись обфусцированного текста
        fileopen = open(file, "w")  # открытие файла
        fileopen.write(filetext)
        fileopen.close()

    # замена instance индентификаторов
    elif ind == "instance":

        # дешифруем instance блоки
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # запись обфусцированного текста
        fileopen = open(file, "w")  # открытие файла
        fileopen.write(filetext)
        fileopen.close()

        # поиск всех instance индентификаторов
        allind = search_instances(file)

        # шифровка instance индентификаторов и создание таблицы соответствия
        encrypt_file(allind, file, filetext, decrypt_table)
        write_decrt_in_file(file, decrypt_table)

    # ошибка
    else:
        print("literal not correct")
        return


# ф-я поиска и замены любых индентификаторов
def allind_search_and_replace(file):

    # обработка ifdef/ifndef
    preobfuscator_ifdef(file)

    # instance индентификаторы (имена)
    instances = search_instances(file)

    # шифруем блоки instance, чтобы они не участвовали далее в обрвботке
    decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()
    fileopen.close()

    defines = re.findall(r"`define +(\w+)", filetext)  # список индентификаторов define

    # список строк с определением или инициализацией базовых индентификаторов
    # в группе хранятся списки индентификаторов
    base = []
    baseindentif = re.findall(
        "\W(?:input|output|inout|wire|reg|"  # список строк с информацией после типа индентификатора
        "parameter|localparam|byte|shortint|"
        "int|integer|longint|bit|logic|shortreal|"
        "real|realtime|time|event"
        ") +(.*?[,;)=])", filetext)

    baseindentif += re.findall(
        "\W(?:input|output|inout|wire|reg|"  # поиск строк со множественным определением
        "parameter|localparam|byte|shortint|"
        "int|integer|longint|bit|logic|shortreal|"
        "real|realtime|time|event"
        ") +.*?,(.*?;)", filetext)

    baseindentif += re.findall(
        "\W(?:input|output|inout|wire|reg|"  # поиск строк с \n в конце
        "parameter|localparam|byte|shortint|"
        "int|integer|longint|bit|logic|shortreal|"
        "real|realtime|time|event"
        ") +([^;,)=\n]+?\n)", filetext)
    # выделение самих индентификаторов из списка baseindentif
    for i in range(len(baseindentif)):
        base += re.findall(r"(\w+) *[,;)=\n]", baseindentif[i])

        # выделение индентификаторов, у которпых в конце [\d:\d]
        base += re.findall(r"(\w+) +\[[\d :]+] *[,;=\n]", baseindentif[i])

    # список строк с блоками enums
    # в 1 группе хранится текст внутри блока
    # во 2 группе хранятся индентификаторы enums
    enumblocks = re.findall(r"enum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", filetext)
    enums = []  # список индентифиакторов внутри блока enums и самих индентификатров определяемых enums
    # цикл обработки enums (выделения индентификаторов из текстов enums)
    for i in range(len(enumblocks)):
        insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # текст внтури блока без присваиваний
        insideind = re.findall(r"(\w+) *", insideWOeq)  # список индентификаторов внутри блока
        outsideind = re.findall(r"(\w+) *",
                                enumblocks[i][1])  # список индентификаторов снаружи блока (объекты enum)
        enumblocks[i] = (insideind + outsideind)
        enums += enumblocks[i]  # в итоге делаем список всех индентификаторов связанных с блоками enum

    structs = re.findall(r"struct[\w|\W]+?} *(\w+);", filetext)  # список индентификаторов struct

    typedefs = re.findall(r"typedef[\w|\W]+?} *(\w+);", filetext)  # список индентификаторов typedef

    # удаление повторных индентификаторов typedef из enums и struct
    for a in structs:
        if a in typedefs:
            structs.remove(a)
    for a in enums:
        if a in typedefs:
            enums.remove(a)

    # поиск индентификаторов, типа typedef'ов
    for typedef in typedefs:
        base_typedef = re.findall(typedef + r" +([\w|\W]*?[,;\n)=])", filetext)
        for i in range(len(base_typedef)):
            base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # добавление найденных индентификаторов в base

    # поиск индентификаторов модулей и функций
    ModuleClusses = re.findall(r"\W(?:module|task|function)[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    # все индентификаторы (без повторов)
    allind = set(defines + base + enums + structs + typedefs + ModuleClusses + instances)  # все индентификаторы

    # шифровка индентификаторов и создание таблицы соответствия
    decrypt_table = {}
    encrypt_file(allind, file, filetext, decrypt_table)

    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

    modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)  # список модулей, описанных в тексте файла

    # заменяем все instance блоки в других файлах, тк мы изменили названия портов функций modules
    change_instances_ports_allf(modules, inv_decrypt_table)

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    # создаем файл с таблицей соответствия
    write_decrt_in_file(file, decrypt_table)

    # дешифруем instance блоки
    for decr_inst in decrypt_table_instances:
        filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

    # шифруем входные данные портов instance блока
    for invdt in inv_decrypt_table:
        ports = set(re.findall(r"\( *"+invdt+r"\W", filetext))
        for port in ports:

            # заменяем некоторые симвылы для правильной задачи регулярного выражения
            port = port.replace("(", r"\(")
            port = port.replace("{", r"\{")
            port = port.replace(".", r"\.")
            port = port.replace("?", r"\?")
            port = port.replace("*", r"\*")
            port = port.replace("|", r"\|")
            port = port.replace("[", r"\[")
            port = port.replace(")", r"\)")
            port = port.replace("]", r"\]")
            port = port.replace("+", r"\+")

            filetext = re.sub(port, "("+inv_decrypt_table[re.search(r"\w+", port)[0]] + port[len(port)-1], filetext)

    
    # заменяем инлентификаторы instance
    for inst in instances:
        filetext = re.sub(inst+r" *\(", inv_decrypt_table[inst]+"(", filetext)
    
    # запись обфусцированного текста
    fileopen = open(file, "w")  # открытие файла
    fileopen.write(filetext)
    fileopen.close()


# ф-я шиврования индентификаторов в тексте
def encrypt_text(allind, filetext, decrypt_table):

    # цикл замены всех индентификаторов
    for ind in allind:
        randlength = random.randint(8, 32)  # выбор случайной длины строки
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, randlength))  # ссоздание случайной строки

        decrypt_table[rand_string] = ind  # добавляем в таблицу новое соответствие новому индентификатору

        filetext = change_ind(filetext, ind, rand_string)

    return filetext


# ф-я записи вместо текста "text" зашиврованного текста в файл "file"
def encrypt_file(allind, file, text, decrypt_table):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()
    fileopen.close()

    # заменяем на зашифрованный текст
    filetext = filetext.replace(text, encrypt_text(allind, text, decrypt_table))

    # записываем его
    fileopen = open(file, "w")  # открытие файла
    fileopen.write(filetext)
    fileopen.close()
    
    
# ф-я создания (или добавление в существующий файл) таблицы замены индентификаторов
def write_decrt_in_file(file, decrypt_table):

    if decrypt_table:
        fileopen = open(file.replace(".sv", "_decrypt_table.txt"), "a")
        fileopen.write(str(decrypt_table)+"\n")
        fileopen.close()


# возращает имена всех instance обьектов
def search_instances(file):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    # все модули и их порты
    modules = scanfiles.getallmodules(os.curdir)

    instances = []  # список instance обьектов

    # цикл поиска instance модуля module из списка modules в файле
    for module in modules:

        # поиск
        searched_instance = re.findall(module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)
        searched_instance += re.findall(module+r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)

        # добавление в список
        if searched_instance:
            instances += searched_instance
        else:
            continue

    # возврат списка имен instance
    return instances
            
            
# ф-я скрывающая (замена на случайную строку) instance блоков, для правильной обработки остального текста
def preobfuscator_instance(file):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    modules = scanfiles.getallmodules(os.curdir)  # все модули проекта

    decrypt_table = {}  # таблица соответствия зашифрованных блоков instance

    # цикл поиска и шиврования блоков instance
    for module in modules:

        # поиск
        searched_instances = re.findall(module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
        searched_instances += re.findall(module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)

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
    fileopen = open(file, "w")  # открытие файла
    fileopen.write(filetext)
    fileopen.close()

    # возврат таблицы соответсвия зашиврованный блоков instance
    return decrypt_table


# ф-я замены названий портов instance обьектов во всех файлах проекта
def change_instances_ports_allf(modules, decr_table):

    files = scanfiles.getsv(os.curdir)  # все файлы

    # цикл изменения портов во всех файлах
    for file in files:

        # обрабатываем ifdef/ifndef
        preobfuscator_ifdef(file)
        
        decrypt_table_instances = {}  # таблица соответствия портов instance обьекта

        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст файла
        fileopen.close()

        # цикл обработки instance обьектов модулей modules
        for module in modules:

            # находим обращения к модулю и заменяем
            ObjWithSubObj = False
            for obj in decr_table:
                filetext = re.sub(module + "\." + obj, decr_table[module]+"." + decr_table[obj], filetext)
                ObjWithSubObj = True
            if not ObjWithSubObj:
                filetext = re.sub(module + "\.", decr_table[module] + ".", filetext)

            # находим все instance обьекты (их текст)
            instances = re.findall(module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
            instances += re.findall(module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)

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
                        instance = instance.replace(module, decr_table[module])
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
        fileopen = open(file, "w")  # открытие файла
        fileopen.write(filetext)
        fileopen.close()


# ф-я поиска портов input/output/inout в тексте
def search_inouts(text):
    inouts = []  # список input/output/inout портов
    inouts += re.findall(r"(?:input|output|inout) +[\w|\W]*?(\w+) *[,;\n)=]", text)
    inouts += re.findall(r"(?:input|output|inout) +[\w|\W]*?(\w+) +\[[\d :]+][,;\n]", text)
    return inouts

def change_ind(text, ind, newind):
    indefic = set(re.findall(r'\W' + ind + r'\W', text))  # поиск всех совпадений с текущим индентификатором
    # ищем именно совпадения с несловесными символами по
    # бокам
    # цикл замены каждого совпадения на случайную строку
    for indef in indefic:
        first = indef[0]  # несловесный символ слева от совпадения
        last = indef[len(indef) - 1]  # несловесный справа слева от совпадения

        # заменяем некоторые симвылы для правильной задачи регулярного выражения
        indef = indef.replace("(", r"\(")
        indef = indef.replace("{", r"\{")
        indef = indef.replace(".", r"\.")
        indef = indef.replace("?", r"\?")
        indef = indef.replace("*", r"\*")
        indef = indef.replace("|", r"\|")
        indef = indef.replace("[", r"\[")
        indef = indef.replace(")", r"\)")
        indef = indef.replace("]", r"\]")
        indef = indef.replace("+", r"\+")

        # замена совпадения на случайную строку
        text = re.sub(indef, first + newind + last, text)

    return text