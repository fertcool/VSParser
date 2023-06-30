import ast
import json
import os
import random
import re
import string

import erase_comments
import ifdefprocessing
import scanfiles


# ���������� ������������ ��� �����������������:
# input / output / inout
# wire / reg
# module / function / task
# instance (������ ������ ������)
# parameter / localparam
# byte / shortint / int / integer / longint / integer / bit / logic / shortreal / real
# realtime / time
# event
# enum / typedef / class
# `define

# ������ ����������
def launch():
    json_file = open(r"obfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.getsv(os.curdir)  # ��������� ����� ����� �������
    else:
        files.append(json_struct["conf"]["filename"])  # ��������� 1 ����������� ����

    # ���������� �� ���� ����������������
    if json_struct["tasks"]["a"]:

        # ���� �� ���� ������
        for file in files:

            json_file_ifdef = open("ifdefprocessing.json", "r")
            json_ifdef_struct = json.load(json_file_ifdef)

            # �������� ��� include �����
            ifdefprocessing.include_for_file(file, json_ifdef_struct)
            # ������������ ifdef/ifndef
            ifdefprocessing.ifdef_pr_forfile(file, json_ifdef_struct)

            #  ������� �����������
            erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

            fileopen = open(file, "r")  # �������� �����
            filetext = fileopen.read()
            fileopen.close()

            defines = re.findall(r"`define +(\w+)", filetext)  # ������ ���������������� define

            # ������ ����� � ������������ ��� �������������� ������� ����������������
            # � ������ �������� ������ ����������������
            base = []
            baseindentif = re.findall(
                "(?:input|output|inout|wire|reg|"  # ������ ����� � ����������� ����� ���� ���������������
                "parameter|localparam|byte|shortint|"
                "int|integer|longint|bit|logic|shortreal|"
                "real|realtime|time|event"
                ") +([\w|\W]*?[,;\n)=])", filetext)

            # ��������� ����� ���������������� �� ������ baseindentif
            for i in range(len(baseindentif)):
                base += re.findall(r"(\w+) *[,;\n)=]", baseindentif[i])

            # ������ ����� � ������� enums
            # � 1 ������ �������� ����� ������ �����
            # �� 2 ������ �������� ��������������� enums
            enumblocks = re.findall(r"enum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", filetext)
            enums = []  # ������ ���������������� ������ ����� enums � ����� ��������������� ������������ enums
            # ���� ��������� enums (��������� ���������������� �� ������� enums)
            for i in range(len(enumblocks)):
                insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # ����� ������ ����� ��� ������������
                insideind = re.findall(r"(\w+) *", insideWOeq)  # ������ ���������������� ������ �����
                outsideind = re.findall(r"(\w+) *",
                                        enumblocks[i][1])  # ������ ���������������� ������� ����� (������� enum)
                enumblocks[i] = (insideind + outsideind)
                enums += enumblocks[i]  # � ����� ������ ������ ���� ���������������� ��������� � ������� enum

            structs = re.findall(r"struct[\w|\W]+?} *(\w+);", filetext)  # ������ ���������������� struct

            typedefs = re.findall(r"typedef[\w|\W]+?} *(\w+);", filetext)  # ������ ���������������� typedef

            # �������� ��������� ���������������� typedef �� enums � struct
            for a in structs:
                if a in typedefs:
                    structs.remove(a)
            for a in enums:
                if a in typedefs:
                    enums.remove(a)

            # ����� ����������������, ���� typedef'��
            for typedef in typedefs:
                base_typedef = re.findall(typedef + r" +([\w|\W]*?[,;\n)=])", filetext)
                for i in range(len(base_typedef)):
                    base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # ���������� ��������� ���������������� � base

            # ����� ���������������� ������� � �������
            ModuleClusses = re.findall(r"(?:module|task|function|class)[\w|\W]*?(\w+) *\(", filetext)


            allind = set(defines + base + enums + structs + typedefs + ModuleClusses)  # ��� ���������������

            # �������� ���������������� � ��������� ������� ������������
            decrypt_table = encrypt(allind, file)

            # ������ ������� ������������ � ����
            fileopen = open(file.replace(".sv", "_decrypt_table.txt"), "w")
            fileopen.write(str(decrypt_table))
            fileopen.close()


# �-� ���������� ����������������
def encrypt(allind, file):
    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    decrypt_table = {}  # ������� ������������

    # ���� ������ ���� ����������������
    for ind in allind:
        randlength = random.randint(8, 32)  # ����� ��������� ����� ������
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, randlength))  # ��������� ��������� ������

        decrypt_table[rand_string] = ind  # ��������� � ������� ����� ������������ ������ ���������������

        indefic = set(re.findall(r'\W' + ind + r'\W', filetext))  # ����� ���� ���������� � ������� ����������������
                                                                  # ���� ������ ���������� � ������������ ��������� ��
                                                                  # �����
        # ���� ������ ������� ���������� �� ��������� ������
        for indef in indefic:
            first = indef[0]  # ����������� ������ ����� �� ����������
            last = indef[len(indef) - 1]  # ����������� ������ ����� �� ����������

            # �������� �������� � ������� ��� ���������� ������ ����������� ���������
            indef = indef.replace("(", r"\(")
            indef = indef.replace("{", r"\{")
            indef = indef.replace(".", r"\.")
            indef = indef.replace("?", r"\?")
            indef = indef.replace("*", r"\*")
            indef = indef.replace("|", r"\|")
            indef = indef.replace("[", r"\[")
            indef = indef.replace(")", r"\)")
            indef = indef.replace("]", r"\]")
            indef = indef.replace("+", r"\+")

            # ������ ���������� �� ��������� ������
            filetext = re.sub(indef, first + rand_string + last, filetext)

    # ������ ������������ ������
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()

    # ������� ������� ������������
    return decrypt_table


# ������� ���������� ����������������
def decrypt(file):
    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()
    decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # �������� ����� ������� ������������
    decrypt_file_opentext = decrypt_file_open.read()  # ����� ������� ������������
    decrypt_file_open.close()

    decrypt_table = ast.literal_eval(decrypt_file_opentext)  # ������� ������������

    # ���� ������ ���������������� �������� ������� ������������
    for indef in decrypt_table:
        filetext = re.sub(indef, decrypt_table[indef], filetext)

    # ������ ������ ������ � ����
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()

