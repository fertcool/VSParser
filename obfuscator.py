import ast
import json
import os
import random
import re
import string

import erase_comments
import ifdefprocessing
import scanfiles


# обфускация производится над индентификаторами:
# input / output / inout
# wire / reg
# module / function / task
# instance (модуль внутри модуля)
# parameter / localparam
# byte / shortint / int / integer / longint / integer / bit / logic / shortreal / real
# realtime / time
# event
# enum / typedef / class
# `define

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

            json_file_ifdef = open("ifdefprocessing.json", "r")
            json_ifdef_struct = json.load(json_file_ifdef)

            # включаем все include файлы
            ifdefprocessing.include_for_file(file, json_ifdef_struct)
            # обрабатываем ifdef/ifndef
            ifdefprocessing.ifdef_pr_forfile(file, json_ifdef_struct)

            #  удаляем комментарии
            erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

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
            ModuleClusses = re.findall(r"(?:module|task|function|class)[\w|\W]*?(\w+) *\(", filetext)


            allind = set(defines + base + enums + structs + typedefs + ModuleClusses)  # все индентификаторы

            # шифровка индентификаторов и получение таблицы соответствия
            decrypt_table = encrypt(allind, file)

            # запись таблицы соответствия в файл
            fileopen = open(file.replace(".sv", "_decrypt_table.txt"), "w")
            fileopen.write(str(decrypt_table))
            fileopen.close()


# ф-я шиврования индентификаторов
def encrypt(allind, file):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    decrypt_table = {}  # таблица соответствия

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
        for indef in indefic:
            first = indef[0]  # несловесный символ слева от совпадения
            last = indef[len(indef) - 1]  # несловесный справа слева от совпадения

            # заменяем скобочки и плюсики для правильной задачи регулярного выражения
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

    # запись шифрованного текста
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()

    # возврат таблицы соответствия
    return decrypt_table


# функция дешивровки индентификаторов
def decrypt(file):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()
    decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # открытие файла таблицы соответствия
    decrypt_file_opentext = decrypt_file_open.read()  # текст таблицы соответствия
    decrypt_file_open.close()

    decrypt_table = ast.literal_eval(decrypt_file_opentext)  # таблица соответствия

    # цикл замены индентификаторов согласно таблице соответствия
    for indef in decrypt_table:
        filetext = re.sub(indef, decrypt_table[indef], filetext)

    # запись нового текста в файл
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()

