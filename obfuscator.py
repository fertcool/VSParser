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

allmodules = scanfiles.getallmodules(os.curdir)

# запуск обфускации
def launch():
    json_file = open(r"obfuscator.json", "r")
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


# ф-я обработки ifdef/ifndef и удаления окмментариев
def preobfuscator_ifdef(file):
    json_file_ifdef = open("ifdefprocessing.json", "r")
    json_ifdef_struct = json.load(json_file_ifdef)

    # включаем все include файлы
    ifdefprocessing.include_for_file(file, json_ifdef_struct)
    # обрабатываем ifdef/ifndef
    ifdefprocessing.ifdef_pr_forfile(file, json_ifdef_struct)

    #  удаляем комментарии
    erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)


def ind_search_and_replace_protect(file):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст всего файла
    fileopen.close()

    protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

    if protectblocks != []:
        # обработка ifdef/ifndef
        preobfuscator_ifdef(file)

        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст всего файла после обработки ifdef/ifndef
        fileopen.close()

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

    moduleblock = re.search(r"module +"+module+r"[\w|\W]+?endmodule *: *"+module+r"[.\n]", filetext)

    if moduleblock != None:

        # обработка ifdef/ifndef
        preobfuscator_ifdef(file)

        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст всего файла после обработки ifdef/ifndef
        fileopen.close()

        moduletext = moduleblock[0]  # текст блока модуля

        fileopen = open(file, "w")  # открытие файла
        fileopen.write(moduletext)
        fileopen.close()

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
        module_ind = re.findall(r"function[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", moduletext)

        # все индентификаторы (без повторов)
        allind = set(defines + base + enums + structs + typedefs + module_ind)  # все индентификаторы

        # удаление из списка allind найденных input/output/inout индентификаторов
        for i in range(len(inouts)):
            if inouts[i] in allind:
                allind.remove(inouts[i])

        # шифровка индентификаторов и создание таблицы соответствия
        encrypt(allind, file)

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

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()
    fileopen.close()

    # шифруем блоки instance, чтобы они не участвовали далее в обработке
    decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

    decrypt_table = {}  # таблица соответствия для замененных индентификаторов

    allind = []  # список всех индентификаторов

    # коррекция
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # если выбранный тип индентификатора - базовый, то проводим соответствующий поиск
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        allinds_str = re.findall(ind + r" +([\w|\W]*?[,;\n)=])", filetext)

        # выделение самих индентификаторов из списка allinds_str
        for i in range(len(allinds_str)):
            allind += re.findall(r"(\w+) *[,;\n)=]", allinds_str[i])

            # выделение индентификаторов, у которпых в конце [\d:\d]
            allind += re.findall(r"(\w+) +\[[\d :]+][,;\n]", allinds_str[i])

        # удаляем  inouts с типом ind из изменяемых
        if ind != "(?:input|output|inout)":
            inouts = search_inouts(filetext)

            # удаляем input/output/inout порты из allind
            for inout in inouts:
                if inout in allind:
                    allind.remove(inout)

        # если обрабатываем input/output/inout порты, то надо в других файлахъ обработать instance
        # блоки соответсвующих модулей
        else:
            # шифровка индентификаторов и создание таблицы соответствия
            write_encrypt_in_file(allind, file, filetext, decrypt_table)

            inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

            modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()",
                                 filetext)  # список модулей, описанных в тексте файла

            # заменяем все instance блоки в других файлах, тк мы изменили названия портов функций modules
            ch_instances_ports_allf(modules, inv_decrypt_table)



    # если выбранный тип индентификатора - module или instance, то проводим соответствующий поиск
    elif ind == "module" or ind == "instance":

        # поиск индентификаторов модулей
        allind = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

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
        "(?:input|output|inout|wire|reg|"  # список строк с информацией после типа индентификатора
        "parameter|localparam|byte|shortint|"
        "int|integer|longint|bit|logic|shortreal|"
        "real|realtime|time|event"
        ") +([\w|\W]*?[,;\n)=])", filetext)



    # выделение самих индентификаторов из списка baseindentif
    for i in range(len(baseindentif)):
        base += re.findall(r"(\w+) *[,;\n)=]", baseindentif[i])

        # выделение индентификаторов, у которпых в конце [\d:\d]
        base += re.findall(r"(\w+) +\[[\d :]+][,;\n]", baseindentif[i])

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

    # поиск индентификаторов модулей и классов
    ModuleClusses = re.findall(r"\W(?:module|task|function)[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    # все индентификаторы (без повторов)
    allind = set(defines + base + enums + structs + typedefs + ModuleClusses + instances)  # все индентификаторы

    # шифровка индентификаторов и создание таблицы соответствия
    decrypt_table = {}
    write_encrypt_in_file(allind, file, filetext, decrypt_table)

    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

    modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)  # список модулей, описанных в тексте файла

    # заменяем все instance блоки в других файлах, тк мы изменили названия портов функций modules
    ch_instances_ports_allf(modules, inv_decrypt_table)

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
        filetext = re.sub(r"\( *"+invdt, "("+inv_decrypt_table[invdt], filetext)

    for inst in instances:
        filetext = filetext.replace(inst, inv_decrypt_table[inst])

    fileopen = open(file, "w")  # открытие файла
    fileopen.write(filetext)
    fileopen.close()



# ф-я шиврования индентификаторов в тексте и создания таблицы соответсвия
def encrypt(allind, filetext, decrypt_table):

    # цикл замены всех индентификаторов
    for ind in allind:
        randlength = random.randint(8, 32)  # выбор случайной длины строки
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, randlength))  # ссоздание случайной строки

        decrypt_table[rand_string] = ind  # добавляем в таблицу новое соответствие новому индентификатору

        indefic = set(re.findall(r'\W' + ind + r'\W', filetext))  # поиск всех совпадений с текущим индентификатором
                                                                  # ищем именно совпадения с несловесными символами по
                                                                  # бокам
        # цикл замены каждого совпадения на случайную строку
        if ind == "scr1_tapc":
            print("sssss")
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
            filetext = re.sub(indef, first + rand_string + last, filetext)

    # # запись шифрованного текста
    # fileopen = open(file, "w")
    # fileopen.write(filetext)
    # fileopen.close()
    #
    # # запись таблицы соответствия в файл
    # fileopen = open(file.replace(".sv", "_decrypt_table.txt"), "w")
    # fileopen.write(str(decrypt_table))
    # fileopen.close()

    return filetext


# ф-я записи вместо текста text зашиврованного текста в файл file
def write_encrypt_in_file(allind, file, text, decrypt_table):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()
    fileopen.close()

    filetext = filetext.replace(text, encrypt(allind, text, decrypt_table))

    fileopen = open(file, "w")  # открытие файла
    fileopen.write(filetext)
    fileopen.close()
def write_decrt_in_file(file, decrypt_table):
    fileopen = open(file.replace(".sv", "_decrypt_table.txt"), "a")
    fileopen.write(str(decrypt_table)+"\n")
    fileopen.close()

# возращает имена всех instance обьектов
def search_instances(file):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    modules = allmodules

    instances = []

    for module in modules:

        searched_instance = re.findall(module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)  # поменять, должен учитывать
        # #(params) имя (inouts)
        searched_instance += re.findall(module+r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)
        if searched_instance != []:
            instances += searched_instance
        else:
            continue

    return instances
            
def preobfuscator_instance(file):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    modules = allmodules

    decrypt_table = {}

    for module in modules:

        searched_instances = re.findall(module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
        searched_instances += re.findall(module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)
        if searched_instances != []:

            for instance_block in searched_instances:

                letters_and_digits = string.ascii_letters + string.digits
                rand_string = ''.join(random.sample(letters_and_digits, 40))  # создание случайной строки

                decrypt_table[rand_string] = instance_block

                filetext = filetext.replace(instance_block, rand_string)

        else:
            continue

    fileopen = open(file, "w")  # открытие файла
    fileopen.write(filetext)
    fileopen.close()

    return decrypt_table

def ch_instances_ports_allf(modules, decr_table):

    files = scanfiles.getsv(os.curdir)

    for file in files:

        preobfuscator_ifdef(file)
        
        decrypt_table_instances = {}

        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст файла
        fileopen.close()

        for module in modules:

            instances = re.findall(module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
            instances += re.findall(module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)
            if instances != []:

                for instance in instances:

                    oldinstance = instance

                    # поиск всех input/output/inout индентификаторов
                    inouts = re.findall(r"\.(\w+) ", instance)

                    for inout in inouts:
                        if inout in decr_table:
                            instance = instance.replace("." + inout + ' ', "." + decr_table[inout] + " ")
                            decrypt_table_instances[decr_table[inout]] = inout
                            
                    instance = instance.replace(module + " ", decr_table[module]+" ")
                    filetext = filetext.replace(oldinstance, instance)

                    decrypt_table_instances[decr_table[module]] = module


            else:
                continue
        
        if decrypt_table_instances != {}:
            write_decrt_in_file(file, decrypt_table_instances)

        fileopen = open(file, "w")  # открытие файла
        fileopen.write(filetext)
        fileopen.close()

def search_inouts(text):
    inouts = []  # список input/output/inout портов
    inouts += re.findall(r"(?:input|output|inout) +[\w|\W]*?(\w+) *[,;\n)=]", text)
    inouts += re.findall(r"(?:input|output|inout) +[\w|\W]*?(\w+) +\[[\d :]+][,;\n]", text)
    return inouts