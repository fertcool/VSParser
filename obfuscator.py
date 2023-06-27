import random
import ast
import re
import json
import scanfiles
import os
import erase_comments
import ifdefprocessing
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

            #  ������� ����������� � �������������
            erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

            fileopen = open(file, "r")  # �������� �����
            filestr = fileopen.read()

            defines = re.findall(r"`define +(\w+)", filestr)
            # ������ ����� � ������������ ��� �������������� ����������������
            # � ������ �������� ������ ����������������
            baseindentif = re.findall(r"\W *(?:input|output|inout|wire|reg|"
                                      r"parameter|localparam|byte|shortint|"
                                      r"int|integer|longint|bit|logic|shortreal|"
                                      r"real|realtime|time|event"
                                      r") +([\w,; \[\]`:-]*?[\n)=])", filestr)
            print("defines = ", defines)
            for i in range(len(baseindentif)):
                baseindentif[i] = re.findall(r"[^`](\w+) *[,;\n)=]", baseindentif[i])
            print("baseindentif = ", baseindentif)

            # ������ ����� � ������� enums
            # � 1 ������ �������� ����� ������ �����
            # �� 2 ������ �������� ��������������� enums
            enums = re.findall(r"enum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", filestr)
            # ���� ��������� enums (��������� ���������������� �� ������� enums)
            for i in range(len(enums)):

                insideWOeq = re.sub(r"=[ \w']+", '', enums[i][0])  # ����� ������ ����� ��� ������������
                insideWOdef = re.sub(r"`ifdef +\w+\n", '', insideWOeq)  # ����� ������ ����� ��� ifdef
                insideWOdef = re.sub(r"`endif *", '', insideWOdef)  # ����� ������ ����� ��� endif

                insideind = re.findall(r"(\w+) *[,;\n)=]", insideWOdef)  # ������ ���������������� ������ �����
                outsideind = re.findall(r"(\w+) *[,;\n)=]", enums[i][1])  # ������ ���������������� ������� ����� (������� enum)
                enums[i] = (insideind+outsideind)  # � ����� ������ ������ ���� ���������������� ��������� � ������� enum
            print("enums = ", enums)
    # file = open("eee.txt", "w")
    # d = {"ddd": "dd", "dsds": "dsds"}
    # string= str(d)
    # aas = ast.literal_eval(string)
    # print(aas["ddd"])
