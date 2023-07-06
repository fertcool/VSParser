import json
import os
import ast
import re
import scanfiles


# запуск деобфускации
def launch():
    json_file = open(r"deobfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.getsv(os.curdir)  # добавляем файлы всего проекта
    else:
        files.append(json_struct["conf"]["filename"])  # добавляем 1 необходимый файл

    # восстановление обфусцированного кода по таблицам соответствия
    if json_struct["tasks"]["a"]:

        # цикл по всем файлам
        for file in files:
            decryptall(file)

    #  Частично восстановить исходный код из обфусцированного только для выбранного класса
    #  идентификаторов (input/output/inout, wire, reg, module, instance, parameter).
    if json_struct["tasks"]["b"]:

        # цикл по всем файлам
        for file in files:
            decrypt_one_ind(file, json_struct["literalclass"])

    # Частично восстановить исходный код из обфусцированного только для портов ввода вывода заданного модуля
    if json_struct["tasks"]["c"]:

        # цикл по всем файлам
        for file in files:
            decrypt_module_inout(file, json_struct["module"])



# функция деобфускации всех индентификаторов
def decryptall(file):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()
    decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # открытие файла таблицы соответствия
    decrypt_file_opentext = decrypt_file_open.read().split("\n")  # текст таблицы соответствия
    decrypt_file_open.close()

    decrypt_file_opentext.pop()
    decrt_list = []
    for decrt_text in decrypt_file_opentext:
        decrt_list.append(ast.literal_eval(decrt_text))

    decrypt_table={}
    for decrt in decrt_list:
        decrypt_table.update(decrt)
    # цикл замены индентификаторов согласно таблице соответствия
    for indef in decrypt_table:
        filetext = re.sub(indef, decrypt_table[indef], filetext)

    # запись нового текста в файл
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()

# ф-я деобфускации выбранного вида индентификаторов (input/output/inout, wire, reg, module, instance, parameter)
def decrypt_one_ind(file, ind):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # открытие файла таблицы соответствия
    decrypt_file_opentext = decrypt_file_open.read()  # текст таблицы соответствия
    decrypt_file_open.close()

    decrypt_table = ast.literal_eval(decrypt_file_opentext)  # таблица соответствия

    allind = []  # список всех индентификаторов

    # коррекция
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # если выбранный тип индентификатора - базовый, то проводим соответствующий поиск
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        inouts = []  # список всех input/output/inout индентификаторов

        # поиск всех input/output/inout индентификаторов
        if ind != "(?:input|output|inout)":

            # поиск всех input/output/inout индентификаторов
            inouts_strs = re.findall(r"(?:input|output|inout) +([\w|\W]*?[,;\n)=])", filetext)

            # выделение самих индентификаторов из списка inouts_strs
            for i in range(len(inouts_strs)):
                inouts += re.findall(r"(\w+) *[,;\n)=]", inouts_strs[i])

                # выделение индентификаторов, у которпых в конце [\d:\d]
                inouts += re.findall(r"(\w+) +\[[\d :]+][,;\n]", inouts_strs[i])

        # поиск всех строк с индентификаторами класса ind
        allinds_str = re.findall(ind + r" +([\w|\W]*?[,;\n)=])", filetext)

        # выделение самих индентификаторов из списка allinds_str
        for i in range(len(allinds_str)):
            allind += re.findall(r"(\w+) *[,;\n)=]", allinds_str[i])

            # выделение индентификаторов, у которпых в конце [\d:\d]
            allind += re.findall(r"(\w+) +\[[\d :]+][,;\n]", allinds_str[i])

        # удаление из списка allind найденных input/output/inout индентификаторов
        for i in range(len(inouts)):
            if inouts[i] in allind:
                allind.remove(inouts[i])

    # если выбранный тип индентификатора - module или instance, то проводим соответствующий поиск
    elif ind == "module" or ind == "instance":

        # поиск индентификаторов модулей
        allind = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    # ошибка
    else:
        print("literal not correct")
        return

    # замена выбранного класса индентификаторов
    for ind in allind:
        if ind in decrypt_table:
            filetext = re.sub(ind, decrypt_table[ind], filetext)

    # запись нового текста в файл
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()


# ф-я деобфускации индентификаторов input/output/inout выбранного модуля
def decrypt_module_inout(file, module):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # открытие файла таблицы соответствия
    decrypt_file_opentext = decrypt_file_open.read()  # текст таблицы соответствия
    decrypt_file_open.close()

    decrypt_table = ast.literal_eval(decrypt_file_opentext)  # таблица соответствия

    moduleblock = re.search(r"module +" + module + r"[\w|\W]+?endmodule *: *" + module + r"[.\n]", filetext)

    # если нашли модуль
    if moduleblock != None:

        moduletext = moduleblock[0]  # текст блока модуля

        inouts = []  # список всех input/output/inout индентификаторов

        # поиск всех input/output/inout индентификаторов
        inouts_strs = re.findall(r"(?:input|output|inout) +([\w|\W]*?[,;\n)=])", moduletext)

        # выделение самих индентификаторов из списка inouts_strs
        for i in range(len(inouts_strs)):
            inouts += re.findall(r"(\w+) *[,;\n)=]", inouts_strs[i])

            # выделение индентификаторов, у которпых в конце [\d:\d]
            inouts += re.findall(r"(\w+) +\[[\d :]+][,;\n]", inouts_strs[i])

            # замена выбранного класса индентификаторов
            for ind in inouts:
                if ind in decrypt_table:
                    filetext = re.sub(ind, decrypt_table[ind], filetext)

            # запись нового текста в файл
            fileopen = open(file, "w")
            fileopen.write(filetext)
            fileopen.close()
    # ошибка
    else:
        print(module + " in " + file + " not found")
        return