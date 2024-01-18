import ast
from work_with_files import *

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

        # объединяем все словари в один
        for decrt in decrt_list:
            decrypt_table.update(decrt)

        return decrypt_table
    else:
        return {}


# ф-я дешифрации некоторых идентификаторов во всех файлах проекта
def change_ind_allf(identifiers):
    from obfuscator.deobfuscator import allfiles
    for file in allfiles:

        filetext = get_file_text(file)  # текст файла

        decrypt_table = get_decrt_in_file(file)

        if decrypt_table:

            for ind in identifiers:
                if ind in decrypt_table:
                    filetext = filetext.replace(ind, decrypt_table[ind])

            # запись измененного текста в файл
            write_text_to_file(file, filetext)
        else:
            continue
