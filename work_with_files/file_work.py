import json
import re


# ------------------------------ФУНКЦИИ_РАБОТЫ_С_ТЕКСТОМ_ФАЙЛА------------------------------ #
def get_json_struct(file):
    json_file = open(file, "r")
    json_struct = json.load(json_file)  # словарь json
    json_file.close()
    return json_struct


# ф-я отдающая текст файла
def get_file_text(file):

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()  # текст файла
    fileopen.close()

    return filetext


# ф-я записи текста в файл
def write_text_to_file(file, text):

    fileopen = open(file, "w")
    fileopen.write(text)
    fileopen.close()


# добавление текста в файл
def add_text_to_file(text, file):

    fileopen = open(file, "a")
    fileopen.write(text + "\n")
    fileopen.close()


# ф-я удаления лишних отступов
def delete_indents(text):
    # убираем лишние отступы
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"( \n)\1+", "\n", text)

    return text