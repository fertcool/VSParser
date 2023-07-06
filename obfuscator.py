# ���������� ������������ ��� �����������������:
# input / output / inout
# wire / reg
# module / function / task
# instance (������ ������ ������)
# parameter / localparam
# byte / shortint / int / integer / longint / integer / bit / logic / shortreal / real
# realtime / time
# event
# enum / typedef
# `define

import ast
import json
import os
import random
import re
import string

import erase_comments
import ifdefprocessing
import scanfiles

allmodules = scanfiles.getallmodules(os.curdir)

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
            allind_search_and_replace(file)

    # ���������� �� ���������� ������ ���������������� (input/output/inout, wire, reg, module, instance, parameter)
    if json_struct["tasks"]["b"]:

        # ���� �� ���� ������
        for file in files:
            ind_search_and_replace(file, json_struct["literalclass"])

    # ���������� �� ���������������� input/output/inout � �������� ������
    if json_struct["tasks"]["c"]:

        # ���� �� ���� ������
        for file in files:
            module_search_and_replace_WOinout(file, json_struct["module"])

    # ���������� � ������ (protect on - protect off)
    if json_struct["tasks"]["d"]:

        # ���� �� ���� ������
        for file in files:
            ind_search_and_replace_protect(file)


# �-� ��������� ifdef/ifndef � �������� ������������
def preobfuscator_ifdef(file):
    json_file_ifdef = open("ifdefprocessing.json", "r")
    json_ifdef_struct = json.load(json_file_ifdef)

    # �������� ��� include �����
    ifdefprocessing.include_for_file(file, json_ifdef_struct)
    # ������������ ifdef/ifndef
    ifdefprocessing.ifdef_pr_forfile(file, json_ifdef_struct)

    #  ������� �����������
    erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)


def ind_search_and_replace_protect(file):
    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� ����� �����
    fileopen.close()

    protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

    if protectblocks != []:
        # ��������� ifdef/ifndef
        preobfuscator_ifdef(file)

        fileopen = open(file, "r")  # �������� �����
        filetext = fileopen.read()  # ����� ����� ����� ����� ��������� ifdef/ifndef
        fileopen.close()

        protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

        for protectblock in protectblocks:
            fileopen = open(file, "r")  # �������� �����
            filetext = fileopen.read()  # ����� ����� ����� ����� ��������� ifdef/ifndef
            fileopen.close()

            # ������ � ���� ������ protect �����
            fileopen = open(file, "w")  # �������� �����
            fileopen.write(protectblock)
            fileopen.close()

            # �������� ��� ��������������� � protect �����
            allind_search_and_replace(file)

            # ������ ������ ������ ������ �� �����
            fileopen = open(file, "r")  # �������� �����
            newprotectblock = fileopen.read()
            fileopen.close()

            # ������ � ���� ������ � ������������ protect ������
            fileopen = open(file, "w")  # �������� �����
            fileopen.write(filetext.replace("`pragma protect on" + protectblock + "`pragma protect off", newprotectblock))
            fileopen.close()
    else:
        return


# �-� ������ � ������ ����� ����������������, ����� input/output/inout � �������� ������
def module_search_and_replace_WOinout(file, module):

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� ����� �����
    fileopen.close()

    moduleblock = re.search(r"module +"+module+r"[\w|\W]+?endmodule *: *"+module+r"[.\n]", filetext)

    if moduleblock != None:

        # ��������� ifdef/ifndef
        preobfuscator_ifdef(file)

        fileopen = open(file, "r")  # �������� �����
        filetext = fileopen.read()  # ����� ����� ����� ����� ��������� ifdef/ifndef
        fileopen.close()

        moduletext = moduleblock[0]  # ����� ����� ������

        fileopen = open(file, "w")  # �������� �����
        fileopen.write(moduletext)
        fileopen.close()

        inouts = search_inouts(moduletext)  # ������ ���� input/output/inout ����������������

        defines = re.findall(r"`define +(\w+)", moduletext)  # ������ ���������������� define

        # ������ ����� � ������������ ��� �������������� ������� ����������������
        # � ������ �������� ������ ����������������
        base = []
        baseindentif = re.findall(
            "(?:wire|reg|"  # ������ ����� � ����������� ����� ���� ���������������
            "parameter|localparam|byte|shortint|"
            "int|integer|longint|bit|logic|shortreal|"
            "real|realtime|time|event"
            ") +([\w|\W]*?[,;\n)=])", moduletext)

        # ��������� ����� ���������������� �� ������ baseindentif
        for i in range(len(baseindentif)):
            base += re.findall(r"(\w+) *[,;\n)=]", baseindentif[i])

            # ��������� ����������������, � �������� � ����� [\d:\d]
            base += re.findall(r"(\w+) +\[[\d :]+][,;\n]", baseindentif[i])

        # ������ ����� � ������� enums
        # � 1 ������ �������� ����� ������ �����
        # �� 2 ������ �������� ��������������� enums
        enumblocks = re.findall(r"enum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", moduletext)
        enums = []  # ������ ���������������� ������ ����� enums � ����� ��������������� ������������ enums
        # ���� ��������� enums (��������� ���������������� �� ������� enums)
        for i in range(len(enumblocks)):
            insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # ����� ������ ����� ��� ������������
            insideind = re.findall(r"(\w+) *", insideWOeq)  # ������ ���������������� ������ �����
            outsideind = re.findall(r"(\w+) *",
                                    enumblocks[i][1])  # ������ ���������������� ������� ����� (������� enum)
            enumblocks[i] = (insideind + outsideind)
            enums += enumblocks[i]  # � ����� ������ ������ ���� ���������������� ��������� � ������� enum

        structs = re.findall(r"struct[\w|\W]+?} *(\w+);", moduletext)  # ������ ���������������� struct

        typedefs = re.findall(r"typedef[\w|\W]+?} *(\w+);", moduletext)  # ������ ���������������� typedef

        # �������� ��������� ���������������� typedef �� enums � struct
        for a in structs:
            if a in typedefs:
                structs.remove(a)
        for a in enums:
            if a in typedefs:
                enums.remove(a)

        # ����� ����������������, ���� typedef'��
        for typedef in typedefs:
            base_typedef = re.findall(typedef + r" +([\w|\W]*?[,;\n)=])", moduletext)
            for i in range(len(base_typedef)):
                base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # ���������� ��������� ���������������� � base

        # ����� ���������������� ������� � �������
        module_ind = re.findall(r"function[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", moduletext)

        # ��� ��������������� (��� ��������)
        allind = set(defines + base + enums + structs + typedefs + module_ind)  # ��� ���������������

        # �������� �� ������ allind ��������� input/output/inout ����������������
        for i in range(len(inouts)):
            if inouts[i] in allind:
                allind.remove(inouts[i])

        # �������� ���������������� � �������� ������� ������������
        encrypt(allind, file)

        # ������ ������ ������ ������ �� �����
        fileopen = open(file, "r")  # �������� �����
        newmoduletext = fileopen.read()
        fileopen.close()

        # ������ � ���� ����� � ������������ ������ module
        fileopen = open(file, "w")  # �������� �����
        fileopen.write(filetext.replace(moduletext, newmoduletext))
        fileopen.close()
    else:
        print(module + " in " + file + " not found")
        return


# �-� ������ � ������ ���������� ���� ���������������� (input/output/inout, wire, reg, module, instance, parameter)
def ind_search_and_replace(file, ind):

    # ��������� ifdef/ifndef
    preobfuscator_ifdef(file)

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()
    fileopen.close()

    # ������� ����� instance, ����� ��� �� ����������� ����� � ���������
    decrypt_table_instances = preobfuscator_instance(file)  # ������� ���������� ������ instance

    decrypt_table = {}  # ������� ������������ ��� ���������� ����������������

    allind = []  # ������ ���� ����������������

    # ���������
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # ���� ��������� ��� ��������������� - �������, �� �������� ��������������� �����
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        allinds_str = re.findall(ind + r" +([\w|\W]*?[,;\n)=])", filetext)

        # ��������� ����� ���������������� �� ������ allinds_str
        for i in range(len(allinds_str)):
            allind += re.findall(r"(\w+) *[,;\n)=]", allinds_str[i])

            # ��������� ����������������, � �������� � ����� [\d:\d]
            allind += re.findall(r"(\w+) +\[[\d :]+][,;\n]", allinds_str[i])

        # �������  inouts � ����� ind �� ����������
        if ind != "(?:input|output|inout)":
            inouts = search_inouts(filetext)

            # ������� input/output/inout ����� �� allind
            for inout in inouts:
                if inout in allind:
                    allind.remove(inout)

        # ���� ������������ input/output/inout �����, �� ���� � ������ ������� ���������� instance
        # ����� �������������� �������
        else:
            # �������� ���������������� � �������� ������� ������������
            write_encrypt_in_file(allind, file, filetext, decrypt_table)

            inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

            modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()",
                                 filetext)  # ������ �������, ��������� � ������ �����

            # �������� ��� instance ����� � ������ ������, �� �� �������� �������� ������ ������� modules
            ch_instances_ports_allf(modules, inv_decrypt_table)



    # ���� ��������� ��� ��������������� - module ��� instance, �� �������� ��������������� �����
    elif ind == "module" or ind == "instance":

        # ����� ���������������� �������
        allind = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    # ������
    else:
        print("literal not correct")
        return




# �-� ������ � ������ ����� ����������������
def allind_search_and_replace(file):

    # ��������� ifdef/ifndef
    preobfuscator_ifdef(file)

    # instance ��������������� (�����)
    instances = search_instances(file)

    # ������� ����� instance, ����� ��� �� ����������� ����� � ���������
    decrypt_table_instances = preobfuscator_instance(file)  # ������� ���������� ������ instance

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

        # ��������� ����������������, � �������� � ����� [\d:\d]
        base += re.findall(r"(\w+) +\[[\d :]+][,;\n]", baseindentif[i])

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
    ModuleClusses = re.findall(r"\W(?:module|task|function)[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    # ��� ��������������� (��� ��������)
    allind = set(defines + base + enums + structs + typedefs + ModuleClusses + instances)  # ��� ���������������

    # �������� ���������������� � �������� ������� ������������
    decrypt_table = {}
    write_encrypt_in_file(allind, file, filetext, decrypt_table)

    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

    modules = re.findall(r"module[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)  # ������ �������, ��������� � ������ �����

    # �������� ��� instance ����� � ������ ������, �� �� �������� �������� ������ ������� modules
    ch_instances_ports_allf(modules, inv_decrypt_table)

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    # ������� ���� � �������� ������������
    write_decrt_in_file(file, decrypt_table)

    # ��������� instance �����
    for decr_inst in decrypt_table_instances:
        filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

    # ������� ������� ������ ������ instance �����
    for invdt in inv_decrypt_table:
        filetext = re.sub(r"\( *"+invdt, "("+inv_decrypt_table[invdt], filetext)

    for inst in instances:
        filetext = filetext.replace(inst, inv_decrypt_table[inst])

    fileopen = open(file, "w")  # �������� �����
    fileopen.write(filetext)
    fileopen.close()



# �-� ���������� ���������������� � ������ � �������� ������� �����������
def encrypt(allind, filetext, decrypt_table):

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
        if ind == "scr1_tapc":
            print("sssss")
        for indef in indefic:
            first = indef[0]  # ����������� ������ ����� �� ����������
            last = indef[len(indef) - 1]  # ����������� ������ ����� �� ����������

            # �������� ��������� ������� ��� ���������� ������ ����������� ���������
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

    # # ������ ������������ ������
    # fileopen = open(file, "w")
    # fileopen.write(filetext)
    # fileopen.close()
    #
    # # ������ ������� ������������ � ����
    # fileopen = open(file.replace(".sv", "_decrypt_table.txt"), "w")
    # fileopen.write(str(decrypt_table))
    # fileopen.close()

    return filetext


# �-� ������ ������ ������ text �������������� ������ � ���� file
def write_encrypt_in_file(allind, file, text, decrypt_table):
    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()
    fileopen.close()

    filetext = filetext.replace(text, encrypt(allind, text, decrypt_table))

    fileopen = open(file, "w")  # �������� �����
    fileopen.write(filetext)
    fileopen.close()
def write_decrt_in_file(file, decrypt_table):
    fileopen = open(file.replace(".sv", "_decrypt_table.txt"), "a")
    fileopen.write(str(decrypt_table)+"\n")
    fileopen.close()

# ��������� ����� ���� instance ��������
def search_instances(file):

    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    modules = allmodules

    instances = []

    for module in modules:

        searched_instance = re.findall(module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)  # ��������, ������ ���������
        # #(params) ��� (inouts)
        searched_instance += re.findall(module+r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)
        if searched_instance != []:
            instances += searched_instance
        else:
            continue

    return instances
            
def preobfuscator_instance(file):
    fileopen = open(file, "r")  # �������� �����
    filetext = fileopen.read()  # ����� �����
    fileopen.close()

    modules = allmodules

    decrypt_table = {}

    for module in modules:

        searched_instances = re.findall(module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
        searched_instances += re.findall(module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)
        if searched_instances != []:

            for instance_block in searched_instances:

                letters_and_digits = string.ascii_letters + string.digits
                rand_string = ''.join(random.sample(letters_and_digits, 40))  # �������� ��������� ������

                decrypt_table[rand_string] = instance_block

                filetext = filetext.replace(instance_block, rand_string)

        else:
            continue

    fileopen = open(file, "w")  # �������� �����
    fileopen.write(filetext)
    fileopen.close()

    return decrypt_table

def ch_instances_ports_allf(modules, decr_table):

    files = scanfiles.getsv(os.curdir)

    for file in files:

        preobfuscator_ifdef(file)
        
        decrypt_table_instances = {}

        fileopen = open(file, "r")  # �������� �����
        filetext = fileopen.read()  # ����� �����
        fileopen.close()

        for module in modules:

            instances = re.findall(module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
            instances += re.findall(module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)
            if instances != []:

                for instance in instances:

                    oldinstance = instance

                    # ����� ���� input/output/inout ����������������
                    inouts = re.findall(r"\.(\w+) ", instance)

                    for inout in inouts:
                        if inout in decr_table:
                            instance = instance.replace("." + inout + ' ', "." + decr_table[inout] + " ")
                            decrypt_table_instances[decr_table[inout]] = inout
                            
                    instance = instance.replace(module + " ", decr_table[module]+" ")
                    filetext = filetext.replace(oldinstance, instance)

                    decrypt_table_instances[decr_table[module]] = module


            else:
                continue
        
        if decrypt_table_instances != {}:
            write_decrt_in_file(file, decrypt_table_instances)

        fileopen = open(file, "w")  # �������� �����
        fileopen.write(filetext)
        fileopen.close()

def search_inouts(text):
    inouts = []  # ������ input/output/inout ������
    inouts += re.findall(r"(?:input|output|inout) +[\w|\W]*?(\w+) *[,;\n)=]", text)
    inouts += re.findall(r"(?:input|output|inout) +[\w|\W]*?(\w+) +\[[\d :]+][,;\n]", text)
    return inouts