import random
import string

import erase_comments
import ifdefprocessing
from obfuscator.search_inds import search_instance_blocks
from work_with_files import *


# ------------------------------¬—ѕќћќ√ј“≈Ћ№Ќџ≈_‘”Ќ ÷»»----------------------------- #

# ф-€ удалени€ из списка allind найденных input/output/inout идентификаторов
def delete_inouts(inouts, allind):
    for i in range(len(inouts)):
        if inouts[i] in allind:
            allind.remove(inouts[i])


# ф-€ обработки ifdef/ifndef и удалени€ комментариев
def preobfuscator_ifdef(file):

    # включаем все include файлы
    ifdefprocessing.include_for_file(file)
    # обрабатываем ifdef/ifndef
    ifdefprocessing.ifdef_pr_forfile(file)

    #  удал€ем комментарии
    erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

    # добавл€ем в начало \n (нужно дл€ правильного поиска идентификаторов)
    filetext = get_file_text(file)
    if filetext[0] != "\n":
        write_text_to_file(file, "\n" + filetext)


# ф-€ скрывающа€ (замена на случайную строку) instance блоков, дл€ правильной обработки остального текста
def preobfuscator_instance(file):
    filetext = get_file_text(file)  # текст файла

    # modules = get_all_modules()  # все модули проекта

    decrypt_table = {}  # таблица соответстви€ зашифрованных блоков instance

    searched_instances = search_instance_blocks(filetext)

    for inst_block in searched_instances:
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, 40))  # создание случайной строки

        # сохран€ем замену в таблице соответстви€
        decrypt_table[rand_string] = inst_block

        # замена в тексте
        filetext = filetext.replace(inst_block, rand_string)

    # запись зашиврованного текста
    write_text_to_file(file, filetext)

    # возврат таблицы соответсви€ зашиврованный блоков instance
    return decrypt_table

