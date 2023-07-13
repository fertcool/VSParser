# ������ ���������� ������ ����� ����������
# ��������� ������������ �������������� � "deobfuscator.json"

import json
import os
import ast
import re
import work_with_files
import obfuscator

allfiles = work_with_files.get_sv_files(os.curdir)  # ��������� ����� ����� �������


# ------------------------------������_������������------------------------------ #

# ������ ������������
def launch():
    json_file = open(r"jsons/deobfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = work_with_files.get_sv_files(os.curdir)  # ��������� ����� ����� �������
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

    # �������� ������������ �������� ��� �� ���������������� ������ ��� ������ ����� ������ ��������� ������
    if json_struct["tasks"]["c"]:

        # ���� �� ���� ������
        for file in files:
            decrypt_module_inout(file, json_struct["module"])


# ------------------------------��������_�������------------------------------ #

# ������� ������������ ���� ��������������� � �����
def decryptall(file):

    filetext = work_with_files.get_file_text(file)  # ����� �����

    # ���� ��� ����� � ��������� ������� � �����, ����� ����� �����a������� �� �� ���� ������
    ports = obfuscator.base_ind_search(filetext, ["input", "output", "inout", "parameter"])

    modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)  # ������ �������, ��������� � ������ �����

    # �������� ������� ������������
    decrypt_table = get_decrt_in_file(file)

    # ���� ������ ��������������� �������� ������� ������������
    for ident in decrypt_table:
        filetext = re.sub(ident, decrypt_table[ident], filetext)

    # ��������������� �����, ����� �������, ��������� �� ���� ������
    change_ind_allf(modules+ports)

    # ������ ������ ������ � ����
    work_with_files.write_text_to_file(file, filetext)


# �-� ������������ ���������� ���� ��������������� (input/output/inout, wire, reg, module, instance, parameter)
def decrypt_one_ind(file, ind):

    filetext = work_with_files.get_file_text(file)  # ����� �����

    decrypt_table = get_decrt_in_file(file)  # ������� ������������

    allind = []  # ������ ���� ���������������

    # ���������
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # ���� ��������� ��� �������������� - �������, �� �������� ��������������� �����
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        inouts = obfuscator.search_inouts(filetext)  # ������ ���� input/output/inout ���������������

        # ����� ���� input/output/inout ���������������
        if ind != "(?:input|output|inout)":

            # ����� ���� ����� � ���������������� ������ ind
            allind = obfuscator.base_ind_search(filetext, [ind])

            # �������� �� ������ allind ��������� input/output/inout ���������������
            obfuscator.delete_inouts(inouts, allind)

        else:

            allind = inouts

    # ���� ��������� ��� �������������� - module ��� instance, �� �������� ��������������� �����
    elif ind == "module":

        # ����� ��������������� �������
        allind = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    elif ind == "instance":

        allind = obfuscator.search_instances(file)

    # ������
    else:
        print("literal not correct")
        return

    # ������ ���������� ������ ���������������
    for indef in allind:
        if indef in decrypt_table:
            filetext = re.sub(indef, decrypt_table[indef], filetext)

    # ������ ��������������� ������ � ����������� �� ���� ������
    if ind == "module" or ind == "(?:input|output|inout)" or ind == "parameter":
        change_ind_allf(allind)

    # ������ ������ ������ � ����
    work_with_files.write_text_to_file(file, filetext)


# �-� ������������ ��������������� input/output/inout ���������� ������
def decrypt_module_inout(file, module):

    filetext = work_with_files.get_file_text(file)  # ����� �����

    decrypt_table = get_decrt_in_file(file)  # ������� ������������

    moduleblock = re.search(r"module +" + module + r"[\w|\W]+?endmodule", filetext)

    # ���� ����� ������
    if moduleblock:

        moduletext = moduleblock[0]  # ����� ����� ������

        inouts = obfuscator.search_inouts(moduletext)

        # ������ ���������� ������ ���������������
        for ind in inouts:
            if ind in decrypt_table:
                filetext = re.sub(ind, decrypt_table[ind], filetext)

        # ������ ������ ������ � ����
        work_with_files.write_text_to_file(file, filetext)

        # �������� ����� � ������ ������
        change_ind_allf(inouts)

    # ������
    else:
        print(module + " in " + file + " not found")
        return


# ------------------------------���������������_�������------------------------------ #

# �-� ��������� ������� ������������ �� ����� (file - ���� ������ ����)
def get_decrt_in_file(file):

    if os.path.isfile(file.replace(".sv", "_decrypt_table.txt")):

        decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # �������� ����� ������� ������������
        decrypt_file_opentext = decrypt_file_open.read().split("\n")  # ������ ������� ������ ������������
        decrypt_file_open.close()

        # ������� ������ ������ �������
        decrypt_file_opentext.pop()

        decrt_list = []  # c����� ������ ������������

        # ���������� �������� � ���� ������
        for decrt_text in decrypt_file_opentext:
            decrt_list.append(ast.literal_eval(decrt_text))

        decrypt_table = {}  # �������� ������� ������������

        # ���������� ��� ������� � ����
        for decrt in decrt_list:
            decrypt_table.update(decrt)

        return decrypt_table
    else:
        return None


# �-� ���������� �������� ��������������� �� ���� ������ �������
def change_ind_allf(identifiers):

    for file in allfiles:

        filetext = work_with_files.get_file_text(file)  # ����� �����

        decrypt_table = get_decrt_in_file(file)

        if decrypt_table:

            for ind in identifiers:
                if ind in decrypt_table:
                    filetext = filetext.replace(ind, decrypt_table[ind])

            # ������ ����������� ������ � ����
            work_with_files.write_text_to_file(file, filetext)
        else:

            continue