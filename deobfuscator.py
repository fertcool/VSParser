import json
import os
import ast
import re
import scanfiles


# ������ ������������
def launch():
    json_file = open(r"deobfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.getsv(os.curdir)  # ��������� ����� ����� �������
    else:
        files.append(json_struct["conf"]["filename"])  # ��������� 1 ����������� ����

    # �������������� ���������������� ���� �� �������� ������������
    if json_struct["tasks"]["a"]:

        # ���� �� ���� ������
        for file in files:
            decryptall(file)

    #  �������� ������������ �������� ��� �� ���������������� ������ ��� ���������� ������
    #  ��������������� (input/output/inout, wire, reg, module, instance, parameter).
    if json_struct["tasks"]["b"]:

        # ���� �� ���� ������
        for file in files:
            decrypt_one_ind(file, json_struct["literalclass"])

    if json_struct["tasks"]["c"]:

        # ���� �� ���� ������
        for file in files:
            decrypt_module_inout(file, json_struct["module"])



# ������� ���������� ����������������
def decryptall(file):
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


def decrypt_one_ind(file, ind):

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # �������� ����� ������� ������������
    decrypt_file_opentext = decrypt_file_open.read()  # ����� ������� ������������
    decrypt_file_open.close()

    decrypt_table = ast.literal_eval(decrypt_file_opentext)  # ������� ������������

    allind = []  # ������ ���� ����������������

    # ���������
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # ���� ��������� ��� ��������������� - �������, �� �������� ��������������� �����
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        inouts = []  # ������ ���� input/output/inout ����������������

        if ind != "(?:input|output|inout)":

            # ����� ���� input/output/inout ����������������
            inouts_strs = re.findall(r"(?:input|output|inout) +([\w|\W]*?[,;\n)=])", filetext)

            # ��������� ����� ���������������� �� ������ inouts_strs
            for i in range(len(inouts_strs)):
                inouts += re.findall(r"(\w+) *[,;\n)=]", inouts_strs[i])

                # ��������� ����������������, � �������� � ����� [\d:\d]
                inouts += re.findall(r"(\w+) +\[[\d :]+][,;\n]", inouts_strs[i])


        allinds_str = re.findall(ind + r" +([\w|\W]*?[,;\n)=])", filetext)

        # ��������� ����� ���������������� �� ������ allinds_str
        for i in range(len(allinds_str)):
            allind += re.findall(r"(\w+) *[,;\n)=]", allinds_str[i])

            # ��������� ����������������, � �������� � ����� [\d:\d]
            allind += re.findall(r"(\w+) +\[[\d :]+][,;\n]", allinds_str[i])

        # �������� �� ������ allind ��������� input/output/inout ����������������
        for i in range(len(inouts)):
            if inouts[i] in allind:
                allind.remove(inouts[i])

    # ���� ��������� ��� ��������������� - module ��� instance, �� �������� ��������������� �����
    elif ind == "module" or ind == "instance":

        # ����� ���������������� �������
        allind = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    # ������
    else:
        print("literal not correct")
        return

    # ������ ���������� ������ ����������������
    for ind in allind:
        if ind in decrypt_table:
            filetext = re.sub(ind, decrypt_table[ind], filetext)

    # ������ ������ ������ � ����
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()


def decrypt_module_inout(file, module):

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # �������� ����� ������� ������������
    decrypt_file_opentext = decrypt_file_open.read()  # ����� ������� ������������
    decrypt_file_open.close()

    decrypt_table = ast.literal_eval(decrypt_file_opentext)  # ������� ������������

    moduleblock = re.search(r"module +" + module + r"[\w|\W]+?endmodule *: *" + module + r"[.\n]", filetext)

    if moduleblock != None:

        moduletext = moduleblock[0]  # ����� ����� ������

        inouts = []  # ������ ���� input/output/inout ����������������

        # ����� ���� input/output/inout ����������������
        inouts_strs = re.findall(r"(?:input|output|inout) +([\w|\W]*?[,;\n)=])", moduletext)

        # ��������� ����� ���������������� �� ������ inouts_strs
        for i in range(len(inouts_strs)):
            inouts += re.findall(r"(\w+) *[,;\n)=]", inouts_strs[i])

            # ��������� ����������������, � �������� � ����� [\d:\d]
            inouts += re.findall(r"(\w+) +\[[\d :]+][,;\n]", inouts_strs[i])

            # ������ ���������� ������ ����������������
            for ind in inouts:
                if ind in decrypt_table:
                    filetext = re.sub(ind, decrypt_table[ind], filetext)

            # ������ ������ ������ � ����
            fileopen = open(file, "w")
            fileopen.write(filetext)
            fileopen.close()