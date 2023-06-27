import random
import ast
import re
import json
import scanfiles
import os
import erase_comments
import ifdefprocessing
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

            #  удаляем комментарии с определениями
            erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

            fileopen = open(file, "r")  # открытие файла
            filestr = fileopen.read()

            defines = re.findall(r"`define +(\w+)", filestr)
            # список строк с определением или инициализацией индентификаторов
            # в группе хранятся списки индентификаторов
            baseindentif = re.findall(r"\W *(?:input|output|inout|wire|reg|"
                                      r"parameter|localparam|byte|shortint|"
                                      r"int|integer|longint|bit|logic|shortreal|"
                                      r"real|realtime|time|event"
                                      r") +([\w,; \[\]`:-]*?[\n)=])", filestr)
            print("defines = ", defines)
            for i in range(len(baseindentif)):
                baseindentif[i] = re.findall(r"[^`](\w+) *[,;\n)=]", baseindentif[i])
            print("baseindentif = ", baseindentif)

            # список строк с блоками enums
            # в 1 группе хранится текст внутри блока
            # во 2 группе хранятся индентификаторы enums
            enums = re.findall(r"enum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", filestr)
            # цикл обработки enums (выделения индентификаторов из текстов enums)
            for i in range(len(enums)):

                insideWOeq = re.sub(r"=[ \w']+", '', enums[i][0])  # текст внтури блока без присваиваний
                insideWOdef = re.sub(r"`ifdef +\w+\n", '', insideWOeq)  # текст внутри блока без ifdef
                insideWOdef = re.sub(r"`endif *", '', insideWOdef)  # текст внутри блока без endif

                insideind = re.findall(r"(\w+) *[,;\n)=]", insideWOdef)  # список индентификаторов внутри блока
                outsideind = re.findall(r"(\w+) *[,;\n)=]", enums[i][1])  # список индентификаторов снаружи блока (объекты enum)
                enums[i] = (insideind+outsideind)  # в итоге делаем список всех индентификаторов связанных с блоками enum
            print("enums = ", enums)
    # file = open("eee.txt", "w")
    # d = {"ddd": "dd", "dsds": "dsds"}
    # string= str(d)
    # aas = ast.literal_eval(string)
    # print(aas["ddd"])
