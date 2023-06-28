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



            json_file_ifdef = open("ifdefprocessing.json", "r")
            json_ifdef_struct = json.load(json_file_ifdef)

            # �������� ��� include �����
            ifdefprocessing.include_for_file(file, json_ifdef_struct)
            # ������������ ifdef/ifndef
            ifdefprocessing.ifdef_pr_forfile(file, json_ifdef_struct)

            #  ������� ����������� � �������������
            erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

            fileopen = open(file, "r")  # �������� �����
            filestr = fileopen.read()

            defines = re.findall(r"`define +(\w+)", filestr)
            print("defines = ", defines)
            # ������ ����� � ������������ ��� �������������� ����������������
            # � ������ �������� ������ ����������������
            base = []
            baseindentif = re.findall(r"[^ \w] *(?:input|output|inout|wire|reg|"
                                      r"parameter|localparam|byte|shortint|"
                                      r"int|integer|longint|bit|logic|shortreal|"
                                      r"real|realtime|time|event"
                                      r") +([\w,; \[\]`:-]*?[\n)=])", filestr)
            for i in range(len(baseindentif)):
                base += re.findall(r"(\w+) *[,;\n)=]", baseindentif[i])
            print("base = ", base)

            # ������ ����� � ������� enums
            # � 1 ������ �������� ����� ������ �����
            # �� 2 ������ �������� ��������������� enums
            enumblocks = re.findall(r"enum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", filestr)
            enums = []
            # ���� ��������� enums (��������� ���������������� �� ������� enums)
            for i in range(len(enumblocks)):

                insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # ����� ������ ����� ��� ������������

                insideind = re.findall(r"(\w+) *", insideWOeq)  # ������ ���������������� ������ �����
                outsideind = re.findall(r"(\w+) *", enumblocks[i][1])  # ������ ���������������� ������� ����� (������� enum)
                enumblocks[i] = (insideind+outsideind)
                enums += enumblocks[i]  # � ����� ������ ������ ���� ���������������� ��������� � ������� enum
            print("enums = ", enums)

            structs = re.findall(r"struct[\w|\W]+?(\w+);", filestr)
            print("structs =", structs)

            typedefs = re.findall(r"typedef[\w|\W]+?(\w+);", filestr)

            for a in structs+enums:
                if a in typedefs:
                    typedefs.remove(a)
            print("typedefs = ", typedefs)

            ModuleClusses = re.findall(r"(?:module|task|function|class) +(\w+)", filestr)
            print("ModuleClasses = ", ModuleClusses)

            allind = defines+base+enums+structs+typedefs+ModuleClusses

def encrypt(allind, filetext):
    return filetext
def decrypt(decr_table, filetext):
    return filetext
    # file = open("eee.txt", "w")
    # d = {"ddd": "dd", "dsds": "dsds"}
    # string= str(d)
    # aas = ast.literal_eval(string)
    # print(aas["ddd"])
