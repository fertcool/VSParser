import json
import os
import ast
import re
import work_with_files
import obfuscator


allfiles = scanfiles.get_sv_files(os.curdir)  # ��������� ����� ����� �������

# ������ ������������
def launch():
    json_file = open(r"jsons/deobfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.get_sv_files(os.curdir)  # ��������� ����� ����� �������
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


# ������� ������������ ���� ���������������� � �����
def decryptall(file):
    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    # ���� ��� ����� � ��������� ������� � �����, ����� ����� ������������ �� �� ���� ������

    # ������ ����� � ������������ ��� �������������� ������� ����������������
    # � ������ �������� ������ ����������������
    ports = []
    ports_indentif = re.findall(
        "(?:input|output|inout|"  # ������ ����� � ����������� ����� ���� ���������������
        "parameter) +([\w|\W]*?[,;\n)=])", filetext)

    # ��������� ����� ���������������� �� ������ baseindentif
    for i in range(len(ports_indentif)):
        ports += re.findall(r"(\w+) *[,;\n)=]", ports_indentif[i])

        # ��������� ����������������, � �������� � ����� [\d:\d]
        ports += re.findall(r"(\w+) +\[[\d :]+][,;\n]", ports_indentif[i])

    modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)  # ������ �������, ��������� � ������ �����

    # �������� ������� ������������
    decrypt_table = get_decrt_in_file(file)

    # ���� ������ ���������������� �������� ������� ������������
    for indef in decrypt_table:
        filetext = re.sub(indef, decrypt_table[indef], filetext)

    change_ind_allf(modules+ports)
    # ������ ������ ������ � ����
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()

# �-� ������������ ���������� ���� ���������������� (input/output/inout, wire, reg, module, instance, parameter)
def decrypt_one_ind(file, ind):

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    decrypt_table = get_decrt_in_file(file)  # ������� ������������

    allind = []  # ������ ���� ����������������

    # ���������
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # ���� ��������� ��� ��������������� - �������, �� �������� ��������������� �����
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        inouts = obfuscator.search_inouts(filetext)  # ������ ���� input/output/inout ����������������

        # ����� ���� input/output/inout ����������������
        if ind != "(?:input|output|inout)":

            # ����� ���� ����� � ����������������� ������ ind
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
        else:
            allind = inouts

    # ���� ��������� ��� ��������������� - module ��� instance, �� �������� ��������������� �����
    elif ind == "module":

        # ����� ���������������� �������
        allind = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    elif ind == "instance":

        allind = obfuscator.search_instances(file)

    # ������
    else:
        print("literal not correct")
        return

    # ������ ���������� ������ ����������������
    for indef in allind:
        if indef in decrypt_table:
            filetext = re.sub(indef, decrypt_table[indef], filetext)

    # ������ ��������������� ������ � ����������� �� ���� ������
    if ind == "module" or ind == "(?:input|output|inout)" or ind == "parameter":
        change_ind_allf(allind)

    # ������ ������ ������ � ����
    fileopen = open(file, "w")
    fileopen.write(filetext)
    fileopen.close()


# �-� ������������ ���������������� input/output/inout ���������� ������
def decrypt_module_inout(file, module):

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    decrypt_file_open = open(file.replace(".sv", "_decrypt_table.txt"), "r")  # �������� ����� ������� ������������
    decrypt_file_opentext = decrypt_file_open.read()  # ����� ������� ������������
    decrypt_file_open.close()

    decrypt_table = ast.literal_eval(decrypt_file_opentext)  # ������� ������������

    moduleblock = re.search(r"module +" + module + r"[\w|\W]+?endmodule", filetext)

    # ���� ����� ������
    if moduleblock:

        moduletext = moduleblock[0]  # ����� ����� ������

        inouts = obfuscator.search_inouts(moduletext)

        # ������ ���������� ������ ����������������
        for ind in inouts:
            if ind in decrypt_table:
                filetext = re.sub(ind, decrypt_table[ind], filetext)

        # ������ ������ ������ � ����
        fileopen = open(file, "w")
        fileopen.write(filetext)
        fileopen.close()

        # �������� ����� � ������ ������
        change_ind_allf(inouts)

    # ������
    else:
        print(module + " in " + file + " not found")
        return


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
def change_ind_allf(identifiers):

    for file in allfiles:

        fileopen = open(file, "r")  # �������� �����
        filetext = fileopen.read()  # ����� �����
        fileopen.close()

        decrypt_table = get_decrt_in_file(file)
        if decrypt_table:

            for ind in identifiers:
                if ind in decrypt_table:
                    filetext = filetext.replace(ind, decrypt_table[ind])

            # ������ ����������� ������ � ����
            fileopen = open(file, "w")  # �������� �����
            fileopen.write(filetext)
            fileopen.close()
        else:
            continue