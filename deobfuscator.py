# СКРИПТ ДЕШИВРОВКИ ФАЙЛОВ ПОСЛЕ ОБФУСКАЦИИ
# настройка конфигурации осуществляется в "deobfuscator.json"

import json
import os
import ast
import re
import work_with_files
import obfuscator

allfiles = work_with_files.get_sv_files(os.curdir)  # добавляем файлы всего проекта


# ------------------------------ЗАПУСК_ДЕОБФУСКАЦИИ------------------------------ #

# запуск деобфускации
def launch():
    json_file = open(r"jsons/deobfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = work_with_files.get_sv_files(os.curdir)  # добавляем файлы всего проекта
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


# ------------------------------ОСНОВНЫЕ_ФУНКЦИИ------------------------------ #

# функция деобфускации всех идентификаторов в файле
def decryptall(file):

    filetext = work_with_files.get_file_text(file)  # текст файла

    # ищем все порты и параметры модулей в файле, чтобы далее расшиaвровать их во всех файлах
    ports = obfuscator.base_ind_search(filetext, ["input", "output", "inout", "parameter"])

    modules = work_with_files.get_modules(filetext)  # список модулей, описанных в тексте файла

    # получаем таблицу соответствия
    decrypt_table = get_decrt_in_file(file)

    # цикл замены идентификаторов согласно таблице соответствия
    for ident in decrypt_table:
        filetext = re.sub(ident, decrypt_table[ident], filetext)

    # расшифвровываем порты, имена модулей, параметры во всех файлах
    change_ind_allf(modules+ports)

    # запись нового текста в файл
    work_with_files.write_text_to_file(file, filetext)


# ф-я деобфускации выбранного вида идентификаторов (input/output/inout, wire, reg, module, instance, parameter)
def decrypt_one_ind(file, ind):

    filetext = work_with_files.get_file_text(file)  # текст файла

    decrypt_table = get_decrt_in_file(file)  # таблица соответствия

    allind = []  # список всех идентификаторов

    # коррекция
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # если выбранный тип идентификатора - базовый, то проводим соответствующий поиск
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        inouts = obfuscator.search_inouts(filetext)  # список всех input/output/inout идентификаторов

        # поиск всех input/output/inout идентификаторов
        if ind != "(?:input|output|inout)":

            # поиск всех строк с идентификаторами класса ind
            allind = obfuscator.base_ind_search(filetext, [ind])

            # удаление из списка allind найденных input/output/inout идентификаторов
            obfuscator.delete_inouts(inouts, allind)

        else:

            allind = inouts

    # если выбранный тип идентификатора - module или instance, то проводим соответствующий поиск
    elif ind == "module":

        # поиск идентификаторов модулей
        allind = work_with_files.get_modules(filetext)

    elif ind == "instance":

        allind = obfuscator.search_instances(filetext)

    # ошибка
    else:
        print("literal not correct")
        return

    # замена выбранного класса идентификаторов
    for indef in allind:
        if indef in decrypt_table:
            filetext = re.sub(indef, decrypt_table[indef], filetext)

    # замена расшифврованных портов и паараметров во всех файлах
    if ind == "module" or ind == "(?:input|output|inout)" or ind == "parameter":
        change_ind_allf(allind)

    # запись нового текста в файл
    work_with_files.write_text_to_file(file, filetext)


# ф-я деобфускации идентификаторов input/output/inout выбранного модуля
def decrypt_module_inout(file, module):

    filetext = work_with_files.get_file_text(file)  # текст файла

    decrypt_table = get_decrt_in_file(file)  # таблица соответствия

    moduleblock = work_with_files.get_module_blocks(filetext, module)

    # если нашли модуль
    if moduleblock:

        moduletext = moduleblock[0]  # текст блока модуля

        inouts = obfuscator.search_inouts(moduletext)

        # замена выбранного класса идентификаторов
        for ind in inouts:
            if ind in decrypt_table:
                filetext = re.sub(ind, decrypt_table[ind], filetext)

        # запись нового текста в файл
        work_with_files.write_text_to_file(file, filetext)

        # заменяем порты в других файлах
        change_ind_allf(inouts)

    # ошибка
    else:
        print(module + " in " + file + " not found")
        return


# ------------------------------ВСПОМОГАТЕЛЬНЫЕ_ФУНКЦИИ------------------------------ #

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
        return {}


# ф-я дешифрации некотрых идентификаторов во всех файлах проекта
def change_ind_allf(identifiers):

    for file in allfiles:

        filetext = work_with_files.get_file_text(file)  # текст файла

        decrypt_table = get_decrt_in_file(file)

        if decrypt_table:

            for ind in identifiers:
                if ind in decrypt_table:
                    filetext = filetext.replace(ind, decrypt_table[ind])

            # запись измененного текста в файл
            work_with_files.write_text_to_file(file, filetext)
        else:

            continue