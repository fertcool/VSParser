import json
import re


# ------------------------------�������_������_�_�������_�����------------------------------ #
def get_json_struct(file):
    json_file = open(file, "r")
    json_struct = json.load(json_file)  # ������� json
    json_file.close()
    return json_struct


# �-� �������� ����� �����
def get_file_text(file):

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    return filetext


# �-� ������ ������ � ����
def write_text_to_file(file, text):

    fileopen = open(file, "w")
    fileopen.write(text)
    fileopen.close()


# ���������� ������ � ����
def add_text_to_file(text, file):

    fileopen = open(file, "a")
    fileopen.write(text + "\n")
    fileopen.close()


# �-� �������� ������ ��������
def delete_indents(text):
    # ������� ������ �������
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"( \n)\1+", "\n", text)

    return text