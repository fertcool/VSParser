import json
import os
import ast
import re
import work_with_files
import obfuscator


allfiles = scanfiles.get_sv_files(os.curdir)  # добавляем файлы всего проекта

# запуск деобфускации
def launch():
    json_file = open(r"jsons/deobfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.get_sv_files(os.curdir)  # добавляем файлы всего проекта
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


# функция деобфускации всех индентификаторов в файле
def decryptall(file):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    # ищем все порты и параметры модулей в файле, чтобы далее расшивровать их во всех файлах

    # список строк с определением или инициализацией базовых индентификаторов
    # в группе хранятся списки индентификаторов
    ports = []
    ports_indentif = re.findall(
        "(?:input|output|inout|"  # список строк с информацией после типа индентификатора
        "parameter) +([\w|\W]*?[,;\n)=])", filetext)

    # выделение самих индентификаторов из списка baseindentif
    for i in range(len(ports_indentif)):
        ports += re.findall(r"(\w+) *[,;\n)=]", ports_indentif[i])

        # выделение индентификаторов, у которпых в конце [\d:\d]
        ports += re.findall(r"(\w+) +\[[\d :]+][,;\n]", ports_indentif[i])

    modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)  # список модулей, описанных в тексте файла

    # получаем таблицу соответствия
    decrypt_table = get_decrt_in_file(file)

    # цикл замены индентификаторов согласно таблице соответствия
    for indef in decrypt_table:
        filetext = re.sub(indef, decrypt_table[indef], filetext)

    change_ind_allf(modules+ports)
    # запись нового текста в файл
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()

# ф-я деобфускации выбранного вида индентификаторов (input/output/inout, wire, reg, module, instance, parameter)
def decrypt_one_ind(file, ind):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    decrypt_table = get_decrt_in_file(file)  # таблица соответствия

    allind = []  # список всех индентификаторов

    # коррекция
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # если выбранный тип индентификатора - базовый, то проводим соответствующий поиск
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        inouts = obfuscator.search_inouts(filetext)  # список всех input/output/inout индентификаторов

        # поиск всех input/output/inout индентификаторов
        if ind != "(?:input|output|inout)":

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
        else:
            allind = inouts

    # если выбранный тип индентификатора - module или instance, то проводим соответствующий поиск
    elif ind == "module":

        # поиск индентификаторов модулей
        allind = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    elif ind == "instance":

        allind = obfuscator.search_instances(file)

    # ошибка
    else:
        print("literal not correct")
        return

    # замена выбранного класса индентификаторов
    for indef in allind:
        if indef in decrypt_table:
            filetext = re.sub(indef, decrypt_table[indef], filetext)

    # замена расшифврованных портов и паараметров во всех файлах
    if ind == "module" or ind == "(?:input|output|inout)" or ind == "parameter":
        change_ind_allf(allind)

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

    moduleblock = re.search(r"module +" + module + r"[\w|\W]+?endmodule", filetext)

    # если нашли модуль
    if moduleblock:

        moduletext = moduleblock[0]  # текст блока модуля

        inouts = obfuscator.search_inouts(moduletext)

        # замена выбранного класса индентификаторов
        for ind in inouts:
            if ind in decrypt_table:
                filetext = re.sub(ind, decrypt_table[ind], filetext)

        # запись нового текста в файл
        fileopen = open(file, "w")
        fileopen.write(filetext)
        fileopen.close()

        # заменяем порты в других файлах
        change_ind_allf(inouts)

    # ошибка
    else:
        print(module + " in " + file + " not found")
        return


# ф-я получения таблицы соответствия из файла (file - файл самого кода)
def get_decrt_in_file(file):

    if os.path.isfile(file.replace(".sv", "_decrypt_table.txt")):

        decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # открытие файла таблицы соответствия
        decrypt_file_opentext = decrypt_file_open.read().split("\n")  # список текстов таблиц соответствия
        decrypt_file_open.close()

        # убираем лишний пустой элемент
        decrypt_file_opentext.pop()

        decrt_list = []  # cписок таблиц соответствия

        # добавление словарей в этот список
        for decrt_text in decrypt_file_opentext:
            decrt_list.append(ast.literal_eval(decrt_text))

        decrypt_table = {}  # итоговая таблица соответствия

        # обьединяем все словари в один
        for decrt in decrt_list:
            decrypt_table.update(decrt)

        return decrypt_table
    else:
        return None
def change_ind_allf(identifiers):

    for file in allfiles:

        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст файла
        fileopen.close()

        decrypt_table = get_decrt_in_file(file)
        if decrypt_table:

            for ind in identifiers:
                if ind in decrypt_table:
                    filetext = filetext.replace(ind, decrypt_table[ind])

            # запись измененного текста в файл
            fileopen = open(file, "w")  # открытие файла
            fileopen.write(filetext)
            fileopen.close()
        else:
            continue