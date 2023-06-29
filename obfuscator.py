import random
import ast
import re
import json
import scanfiles
import os
import erase_comments
import ifdefprocessing
import string

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

            #  удаляем комментарии с определениями
            erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

            fileopen = open(file, "r")  # открытие файла
            filetext = fileopen.read()
            fileopen.close()

            defines = re.findall(r"`define +(\w+)", filetext)
            print("defines = ", defines)
            # список строк с определением или инициализацией индентификаторов
            # в группе хранятся списки индентификаторов
            base = []
            baseindentif = re.findall("(?:input|output|inout|wire|reg|"
                                      "parameter|localparam|byte|shortint|"
                                      "int|integer|longint|bit|logic|shortreal|"
                                      "real|realtime|time|event"
                                      ") +([\w|\W]*?[,;\n)=])", filetext)
            print(baseindentif)
            for i in range(len(baseindentif)):
                base += re.findall(r"(\w+) *[,;\n)=]", baseindentif[i])
            print("base = ", base)

            # список строк с блоками enums
            # в 1 группе хранится текст внутри блока
            # во 2 группе хранятся индентификаторы enums
            enumblocks = re.findall(r"enum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", filetext)
            enums = []
            # цикл обработки enums (выделения индентификаторов из текстов enums)
            for i in range(len(enumblocks)):
                insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # текст внтури блока без присваиваний
                insideind = re.findall(r"(\w+) *", insideWOeq)  # список индентификаторов внутри блока
                outsideind = re.findall(r"(\w+) *", enumblocks[i][1])  # список индентификаторов снаружи блока (объекты enum)
                enumblocks[i] = (insideind+outsideind)
                enums += enumblocks[i]  # в итоге делаем список всех индентификаторов связанных с блоками enum
            print("enums = ", enums)

            structs = re.findall(r"struct[\w|\W]+?(\w+);", filetext)
            print("structs =", structs)

            typedefs = re.findall(r"typedef[\w|\W]+?(\w+);", filetext)

            for a in structs:
                if a in typedefs:
                    structs.remove(a)
            for a in enums:
                if a in typedefs:
                    enums.remove(a)
            print("typedefs = ", typedefs)

            # поиск индентификаторов, типа typedef'ов

            for typedef in typedefs:
                base_typedef = re.findall(typedef+r" +([\w|\W]*?[,;\n)=])", filetext)
                for i in range(len(base_typedef)):
                    base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])
                    print(re.findall(r"(\w+) *[,;\n)=]", base_typedef[i]))

            ModuleClusses = re.findall(r"(?:module|task|function|class) +(\w+)", filetext)
            print("ModuleClasses = ", ModuleClusses)

            allind = defines+base+enums+structs+typedefs+ModuleClusses

            encrypt_table = encrypt(allind, file)

            print(encrypt_table)



def encrypt(allind, file):
    fileopen = open(file, "r")
    filetext = fileopen.read()
    fileopen.close()

    encrypt_table = {}
    for ind in allind:
        randlength = random.randint(8, 32)
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, randlength))

        encrypt_table[rand_string] = ind


        pattern1 = r'(\W)' + ind + r'(\W)'
        pattern2 = r'\1' + rand_string + r'\2'

        indefic = set(re.findall(r'\W' + ind + r'\W', filetext))

        for indef in indefic:
            first = indef[0]
            last = indef[len(indef)-1]

            indef = indef.replace("(", r"\(")
            indef = indef.replace(")", r"\)")

            filetext = re.sub(indef, first + rand_string + last, filetext)

        # filetext = re.sub(pattern1, pattern2, filetext)

    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()

    return encrypt_table
    
def decrypt(decr_table, file):
    return file
    # file = open("eee.txt", "w")
    # d = {"ddd": "dd", "dsds": "dsds"}
    # string= str(d)
    # aas = ast.literal_eval(string)
    # print(aas["ddd"])
