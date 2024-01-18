import random
import string
from work_with_files import *

# ------------------------------‘”Ќ ÷»»_Ў»‘–ќ¬јЌ»я------------------------------ #


# ф-€ шивровани€ идентификаторов в тексте
def encrypt_text(allind, filetext, decrypt_table):
    # цикл замены всех идентификаторов
    for ind in allind:
        randlength = random.randint(8, 32)  # выбор случайной длины строки
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, randlength))  # ссоздание случайной строки

        decrypt_table[rand_string] = ind  # добавл€ем в таблицу новое соответствие новому идентификатору

        # запись в текст нового идентификатора
        filetext = change_ind(filetext, ind, rand_string)

    return filetext


# ф-€ записи вместо текста "text" зашиврованного текста в файл "file"
def encrypt_file(allind, file, text, decrypt_table):
    filetext = get_file_text(file)  # текст файла

    # замен€ем на зашифрованный текст
    filetext = filetext.replace(text, encrypt_text(allind, text, decrypt_table))

    # записываем его
    write_text_to_file(file, filetext)


# ф-€ создани€ (или добавление в существующий файл) таблицы замены идентификаторов
def write_decrt_in_file(file, decrypt_table):
    if decrypt_table:
        add_text_to_file(str(decrypt_table), file.replace(".sv", "_decrypt_table.txt"))


# ф-€ замены идентификаторов в тексте на новые
def change_ind(text, ind, newind):
    indefic = set(re.findall(r'\W' + ind + r'\W', text))  # поиск всех совпадений с текущим идентификатором
    # ищем именно совпадени€ с несловесными символами по
    # бокам
    # цикл замены каждого совпадени€ на случайную строку
    for indef in indefic:
        first = indef[0]  # несловесный символ слева от совпадени€
        last = indef[-1]  # несловесный справа от совпадени€

        # замен€ем некоторые символы дл€ правильной задачи регул€рного выражени€
        indef = regexp_to_str(indef)

        # замена совпадени€ на случайную строку
        text = re.sub(indef, first + newind + last, text)

    return text


# ф-€ замен€юща€ регул€рное выражение со спец. символами в обычную строку
def regexp_to_str(regexp):
    # замен€ем некоторые симвылы дл€ правильной задачи регул€рного выражени€
    regexp = regexp.replace("(", r"\(")
    regexp = regexp.replace("{", r"\{")
    regexp = regexp.replace(".", r"\.")
    regexp = regexp.replace("?", r"\?")
    regexp = regexp.replace("*", r"\*")
    regexp = regexp.replace("|", r"\|")
    regexp = regexp.replace("[", r"\[")
    regexp = regexp.replace(")", r"\)")
    regexp = regexp.replace("]", r"\]")
    regexp = regexp.replace("+", r"\+")

    return regexp