# ������ ���������� ������
# ��������� ������������ �������������� � "obfuscator.json"

# ���������� ������������ ��� ����������������:
# input / output / inout
# wire / reg
# module / function / task
# instance
# parameter / localparam
# byte / shortint / int / integer / longint / integer / bit / logic / shortreal / real
# realtime / time
# event
# enum / typedef
# `define
# ���������� �� ������������ ��� �������� instance �������� ����� "."


import json
import os
import random
import re
import string
import erase_comments
import ifdefprocessing
import work_with_files


# ------------------------------������_����������------------------------------ #

def launch():
    json_file = open(r"jsons/obfuscator.json", "r")
    json_struct = json.load(json_file)

    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = work_with_files.get_sv_files(os.curdir)  # ��������� ����� ����� �������
    else:
        files.append(json_struct["conf"]["filename"])  # ��������� 1 ����������� ����

    # ���������� �� ���� ���������������
    if json_struct["tasks"]["a"]:

        # ���� �� ���� ������
        for file in files:
            allind_search_and_replace(file)

    # ���������� �� ���������� ������ ��������������� (input/output/inout, wire, reg, module, instance, parameter)
    if json_struct["tasks"]["b"]:

        # ���� �� ���� ������
        for file in files:
            ind_search_and_replace(file, json_struct["literalclass"])

    # ���������� �� ��������������� input/output/inout � �������� ������
    if json_struct["tasks"]["c"]:

        # ���� �� ���� ������
        for file in files:
            module_search_and_replace_wo_inout(file, json_struct["module"])

    # ���������� � ������ (protect on - protect off)
    if json_struct["tasks"]["d"]:

        # ���� �� ���� ������
        for file in files:
            ind_search_and_replace_protect(file)


# ------------------------------��������_�������------------------------------ #

# �-� ���������� ������ � �������� `pragma protect on - `pragma protect off
def ind_search_and_replace_protect(file):
    filetext = work_with_files.get_file_text(file)  # ����� �����

    # ����� ��������������� ����� ����
    protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

    if protectblocks:
        # ��������� ifdef/ifndef
        preobfuscator_ifdef(file)

        filetext = work_with_files.get_file_text(file)  # ����� ����� ����� ����� ��������� ifdef/ifndef

        # ��������� �����, �.�. ������� ��������� ifdef/ifndef
        protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

        # ���� ��������� ������ ����
        for protectblock in protectblocks:
            filetext = work_with_files.get_file_text(file)  # ����� ����� ����� ����� ��������� ifdef/ifndef

            # ������ � ���� ������ protect �����
            work_with_files.write_text_to_file(file, protectblock)

            # �������� ��� �������������� � protect �����
            allind_search_and_replace(file)

            # ������ ������ ������ ������ �� �����
            newprotectblock = work_with_files.get_file_text(file)

            # ������ � ���� ������ � ������������ protect ������
            work_with_files.write_text_to_file(file, filetext.replace("`pragma protect on" + protectblock
                                                                      + "`pragma protect off", newprotectblock))

    else:
        return


# �-� ������ � ������ ����� ���������������, ����� input/output/inout � �������� ������
def module_search_and_replace_wo_inout(file, module):
    filetext = work_with_files.get_file_text(file)  # ����� �����

    moduleblock = re.search(r"\Wmodule +" + module + r"[\w|\W]+?endmodule", filetext)

    # ���� ����� ������, �� ������������ ���
    if moduleblock:

        # ��������� ifdef/ifndef
        preobfuscator_ifdef(file)

        moduletext = re.search(r"\Wmodule +" + module + r"[\w|\W]+?endmodule", filetext)[0]  # ����� ����� ������

        # ������ ������ � ����� (�� ������ ������� ���� ����� ������ �������������� ������)
        work_with_files.write_text_to_file(file, moduletext)

        # ������� ����� instance, ����� ��� �� ����������� ����� � ���������
        decrypt_table_instances = preobfuscator_instance(file)  # ������� ���������� ������ instance

        newmoduletext = work_with_files.get_file_text(file)  # ����� ������ ����� �������� instance ��������

        # instance �������������� (�����)
        instances = search_instances(file)

        inouts = search_inouts(newmoduletext)  # ������ ���� input/output/inout ���������������

        defines = re.findall(r"`define +(\w+)", newmoduletext)  # ������ ��������������� define

        # ������ ����� � ������������ ��� �������������� ������� ���������������
        # � ������ �������� ������ ���������������
        base = base_ind_search(newmoduletext, ["wire", "reg", "parameter", "localparam", "byte", "shortint",
                                               "int", "integer", "longint", "bit", "logic", "shortreal",
                                               "real", "realtime", "time", "event"])

        enums = enum_ind_search(newmoduletext)  # �������������� enums

        structs = re.findall(r"\Wstruct[\w|\W]+?} *(\w+);", newmoduletext)  # ������ ��������������� struct

        typedefs = re.findall(r"\Wtypedef[\w|\W]+?} *(\w+);", newmoduletext)  # ������ ��������������� typedef

        # �������� ��������� ��������������� typedef �� enums � struct
        for a in structs:
            if a in typedefs:
                structs.remove(a)
        for a in enums:
            if a in typedefs:
                enums.remove(a)

        # ����� ���������������, ���� typedef'��
        for typedef in typedefs:
            base_typedef = re.findall(typedef + r" +(.*?[,;\n)=])", newmoduletext)
            for i in range(len(base_typedef)):
                base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # ���������� ��������� ��������������� � base

        # ����� ��������������� �������
        module_ind = re.findall(r"\W(?:function|task)[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", newmoduletext)

        # ��� �������������� (��� ��������)
        allind = set(defines + base + enums + structs + typedefs + module_ind + instances)  # ��� ��������������

        # �������� �� ������ allind ��������� input/output/inout ���������������
        delete_inouts(inouts, allind)

        # �������� ��������������� � �������� ������� ������������
        decrypt_table = {}
        encrypt_file(allind, file, newmoduletext, decrypt_table)

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

        # ��������� ���� �� � ������ ���������
        modules = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?#\(",
                             newmoduletext)  # ������ �������, ��������� � ������ �����
        # ���� �����, �� �������� �� � ������ ������
        if modules:
            # �������� ��� instance ����� � ������ ������ (������ ���������)
            change_instances_ports_allf(modules, inv_decrypt_table)

        # ������ ������ ������ ������ �� �����
        newmoduletext = work_with_files.get_file_text(file)

        # ��������� instance �����
        for decr_inst in decrypt_table_instances:
            newmoduletext = newmoduletext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # �������� �������������� instance
        for inst in instances:
            newmoduletext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", newmoduletext)

        # ������� ���� � �������� ������������
        write_decrt_in_file(file, decrypt_table)

        # ������ � ���� ����� � ������������ ������ module
        work_with_files.write_text_to_file(file, filetext.replace(moduletext, newmoduletext))
    else:
        print(module + " in " + file + " not found")
        return


# �-� ������ � ������ ���������� ���� ��������������� (input/output/inout, wire, reg, module, instance, parameter)
def ind_search_and_replace(file, ind):
    # ��������� ifdef/ifndef
    preobfuscator_ifdef(file)

    # ������� ����� instance, ����� ��� �� ����������� ����� � ���������
    decrypt_table_instances = preobfuscator_instance(file)  # ������� ���������� ������ instance

    filetext = work_with_files.get_file_text(file)  # ����� �����

    decrypt_table = {}  # ������� ������������ ��� ���������� ���������������

    allind = []  # ������ ���� ���������������

    # ���������
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # ���� ��������� ��� �������������� - "�������", �� �������� ��������������� �����
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        # ����� ���� ��������������� ���� ind
        allind = base_ind_search(filetext, [ind])

        # ������������ �� �����
        if ind != "(?:input|output|inout)":

            # ������������ parameter
            if ind == "parameter":

                # �������� ���������������
                encrypt_file(allind, file, filetext, decrypt_table)

                # ���� ������ � �����������
                modules = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?#\(",
                                     filetext)  # ������ �������, ��������� � ������ �����
                # ���� �����, �� �������� �� � ������ ������
                if modules:
                    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

                    # �������� ��� instance ����� � ������ ������ (������ ���������)
                    change_instances_ports_allf(modules, inv_decrypt_table)

                # ������� ���� � �������� ������������
                write_decrt_in_file(file, decrypt_table)

                filetext = work_with_files.get_file_text(file)  # ����� �����

                # ��������� instance �����
                for decr_inst in decrypt_table_instances:
                    filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

                # ������ ���������������� ������
                work_with_files.write_text_to_file(file, filetext)

            # ������������ reg, wire
            else:
                inouts = search_inouts(filetext)

                # ������� input/output/inout ����� �� allind
                delete_inouts(inouts, allind)

                # �������� ��������������� � �������� ������� ������������
                encrypt_file(allind, file, filetext, decrypt_table)
                write_decrt_in_file(file, decrypt_table)

        # ���� ������������ input/output/inout �����, �� ���� � ������ ������ ���������� ����� instance
        # �������� �������������� �������
        else:
            # �������� ���������������
            encrypt_file(allind, file, filetext, decrypt_table)

            inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

            modules = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()",
                                 filetext)  # ������ �������, ��������� � ������ �����

            # �������� ��� instance ����� � ������ ������, �� �� �������� �������� ������ ������� modules
            change_instances_ports_allf(modules, inv_decrypt_table)

            filetext = work_with_files.get_file_text(file)  # ����� �����

            # ������� ���� � �������� ������������
            write_decrt_in_file(file, decrypt_table)

            # ��������� instance �����
            for decr_inst in decrypt_table_instances:
                filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

            # ������ ���������������� ������
            work_with_files.write_text_to_file(file, filetext)

    # ���� ��������� ��� �������������� module - �� �������� �������������� ������� � ���
    # instance �������� � ������ ������
    elif ind == "module":

        # ����� ��������������� �������
        allind = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

        # �������� ���������������
        encrypt_file(allind, file, filetext, decrypt_table)

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

        # �������� ��� ���� instance ������ � ������ ������
        change_instances_ports_allf(allind, inv_decrypt_table)

        # ������� ���� � �������� ������������
        write_decrt_in_file(file, decrypt_table)

        filetext = work_with_files.get_file_text(file)  # ����� �����

        # ��������� instance �����
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # ������ ���������������� ������
        work_with_files.write_text_to_file(file, filetext)

    # ������ instance ���������������
    elif ind == "instance":

        # ��������� instance �����
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # ������ ������ ����� ����������
        work_with_files.write_text_to_file(file, filetext)

        # ����� ���� instance ���������������
        allind = search_instances(file)

        # �������� instance ��������������� � �������� ������� ������������
        encrypt_text(allind, "", decrypt_table)
        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������
        for inst in allind:
            filetext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", filetext)

        # ������ ���������������� ������
        work_with_files.write_text_to_file(file, filetext)

        write_decrt_in_file(file, decrypt_table)

    # ������
    else:
        print("literal not correct")
        return


# �-� ������ � ������ ����� ���������������
def allind_search_and_replace(file):
    # ��������� ifdef/ifndef
    preobfuscator_ifdef(file)

    # instance �������������� (�����)
    instances = search_instances(file)

    # ������� ����� instance, ����� ��� �� ����������� ����� � ���������
    decrypt_table_instances = preobfuscator_instance(file)  # ������� ���������� ������ instance

    filetext = work_with_files.get_file_text(file)  # ����� ����� ����� ifdef ��������� � �������� instance ��������

    defines = re.findall(r"`define +(\w+)", filetext)  # ������ ��������������� define

    # ������ ����� � ������������ ��� �������������� ������� ���������������
    # � ������ �������� ������ ���������������
    base = base_ind_search(filetext, ["input", "output", "inout", "wire", "reg",
                                      "parameter", "localparam", "byte", "shortint",
                                      "int", "integer", "longint", "bit", "logic", "shortreal",
                                      "real", "realtime", "time", "event"])

    enums = enum_ind_search(filetext)  # ������ ��������������� enums

    structs = re.findall(r"\Wstruct[\w|\W]+?} *(\w+);", filetext)  # ������ ��������������� struct

    typedefs = re.findall(r"\Wtypedef[\w|\W]+?} *(\w+);", filetext)  # ������ ��������������� typedef

    # �������� ��������� ��������������� typedef �� enums � struct
    for a in structs:
        if a in typedefs:
            structs.remove(a)
    for a in enums:
        if a in typedefs:
            enums.remove(a)

    # ����� ���������������, ���� typedef'��
    for typedef in typedefs:
        base_typedef = re.findall(typedef + r" +(.*?[,;\n)=])", filetext)
        for i in range(len(base_typedef)):
            base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # ���������� ��������� ��������������� � base

    # ����� ��������������� ������� � �������
    ModuleClusses = re.findall(r"\W(?:module|task|function)[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()", filetext)

    # ��� �������������� (��� ��������)
    allind = set(defines + base + enums + structs + typedefs + ModuleClusses + instances)  # ��� ��������������

    # �������� ��������������� � �������� ������� ������������
    decrypt_table = {}
    encrypt_file(allind, file, filetext, decrypt_table)

    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

    modules = re.findall(r"\Wmodule[\w|\W]*?(\w+)[ \n]*?(?:\(|#\()",
                         filetext)  # ������ �������, ��������� � ������ �����

    # �������� ��� instance ����� � ������ ������, �� �� �������� �������� ������ ������� modules
    change_instances_ports_allf(modules, inv_decrypt_table)

    filetext = work_with_files.get_file_text(file)  # ����� ����� ����� �������� ����� ���������������

    # ������� ���� � �������� ������������
    write_decrt_in_file(file, decrypt_table)

    # ��������� instance �����
    for decr_inst in decrypt_table_instances:
        filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

    # ������� ������� ������ ������ instance �����
    for invdt in inv_decrypt_table:
        ports = set(re.findall(r"\( *" + invdt + r"\W", filetext))
        for port in ports:
            # �������� ��������� ������� ��� ���������� ������ ����������� ���������
            port = regexp_to_str(port)

            filetext = re.sub(port, "(" + inv_decrypt_table[re.search(r"\w+", port)[0]] + port[-1], filetext)

    # �������� ��������������� instance
    for inst in instances:
        filetext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", filetext)

    # ������ ���������������� ������
    work_with_files.write_text_to_file(file, filetext)


# �-� ������ �������� ������ instance ��������, �� � ����� �� ���� ������ �������
def change_instances_ports_allf(modules, decr_table):
    files = work_with_files.get_sv_files(os.curdir)  # ��� �����

    # ���� ��������� ������ �� ���� ������
    for file in files:

        # ������������ ifdef/ifndef
        preobfuscator_ifdef(file)

        decrypt_table_instances = {}  # ������� ������������ ������ instance �������

        filetext = work_with_files.get_file_text(file)  # ����� �����

        # ���� ��������� instance �������� ������� modules
        for module in modules:

            # ������� ��� instance ������� (�� �����)
            instances = re.findall(r"\W" + module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
            instances += re.findall(r"\W" + module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)

            # ���� ����� ������� ����������, �� ������������ ��
            if instances:

                # ���� ��������� ������ ������� instance
                for instance in instances:

                    # ��������� ������ ����� �������
                    oldinstance = instance

                    # ����� ���� ������ �������
                    inouts = re.findall(r"\.(\w+)", instance)

                    # ���� ������ �������� ������ �� ��������������� � ������� decr_table
                    for inout in inouts:
                        if inout in decr_table:
                            instance = change_ind(instance, inout, decr_table[inout])

                            # ��������� � ������� decrypt_table_instances ��������������� ������ �� decr_table
                            decrypt_table_instances[decr_table[inout]] = inout

                    # ���� ���������� - �������� �������� ������ instance ������� � ��������� � �������
                    # decrypt_table_instances
                    if module in decr_table:
                        instance = re.sub(module, decr_table[module], instance, 1)  # �������� ������ 1 ���������
                        decrypt_table_instances[decr_table[module]] = module

                    # �������� ����� �� ����������
                    filetext = filetext.replace(oldinstance, instance)

            # ���� ����� �������� ���, �� ���������� �����
            else:
                continue
        # ���� ������� decrypt_table_instances �� �����, �� ���������� �� � ���� ������ ������������
        if decrypt_table_instances:
            write_decrt_in_file(file, decrypt_table_instances)

        # ������ ����������� ������ � ����
        work_with_files.write_text_to_file(file, filetext)


# ------------------------------�������_����������------------------------------ #

# �-� ���������� ��������������� � ������
def encrypt_text(allind, filetext, decrypt_table):
    # ���� ������ ���� ���������������
    for ind in allind:
        randlength = random.randint(8, 32)  # ����� ��������� ����� ������
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, randlength))  # ��������� ��������� ������

        decrypt_table[rand_string] = ind  # ��������� � ������� ����� ������������ ������ ��������������

        filetext = change_ind(filetext, ind, rand_string)

    return filetext


# �-� ������ ������ ������ "text" �������������� ������ � ���� "file"
def encrypt_file(allind, file, text, decrypt_table):
    filetext = work_with_files.get_file_text(file)  # ����� �����

    # �������� �� ������������� �����
    filetext = filetext.replace(text, encrypt_text(allind, text, decrypt_table))

    # ���������� ���
    work_with_files.write_text_to_file(file, filetext)


# �-� �������� (��� ���������� � ������������ ����) ������� ������ ���������������
def write_decrt_in_file(file, decrypt_table):
    if decrypt_table:
        work_with_files.add_text_to_file(str(decrypt_table), file.replace(".sv", "_decrypt_table.txt"))


# �-� ������ ��������������� � ������ �� �����
def change_ind(text, ind, newind):
    indefic = set(re.findall(r'\W' + ind + r'\W', text))  # ����� ���� ���������� � ������� ���������������
    # ���� ������ ���������� � ������������ ��������� ��
    # �����
    # ���� ������ ������� ���������� �� ��������� ������
    for indef in indefic:
        first = indef[0]  # ����������� ������ ����� �� ����������
        last = indef[-1]  # ����������� ������ ����� �� ����������

        # �������� ��������� ������� ��� ���������� ������ ����������� ���������
        indef = regexp_to_str(indef)

        # ������ ���������� �� ��������� ������
        text = re.sub(indef, first + newind + last, text)

    return text


# �-� ���������� ���������� ��������� �� ����. ��������� � ������� ������
def regexp_to_str(regexp):
    # �������� ��������� ������� ��� ���������� ������ ����������� ���������
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


# ------------------------------�������_������_���������������----------------------------- #

# ��������� ����� ���� instance ��������
def search_instances(file):
    filetext = work_with_files.get_file_text(file)  # ����� �����

    # ��� ������ � �� �����
    modules = work_with_files.get_all_modules(os.curdir)

    instances = []  # ������ instance ��������

    # ���� ������ instance ������ module �� ������ modules � �����
    for module in modules:

        # �����
        searched_instance = re.findall(r"\W" + module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)
        searched_instance += re.findall(r"\W" + module + r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)

        # ���������� � ������
        if searched_instance:
            instances += searched_instance
        else:
            continue

    # ������� ������ ���� instance
    return instances


# �-� ������ ������ input/output/inout � ������
def search_inouts(text):
    inouts = base_ind_search(text, ["(?:input|output|inout)"])  # ������ input/output/inout ������

    return inouts


# �-� ������������ ������ ������� �������� (��� ��������) ��������������� � ������
def base_ind_search(text, ind_list):
    base_ind_pattern = ind_list[0]

    # ������ ����������� ��������� ��� ���������� ������ ������ �� ���������������
    if len(ind_list) > 1:
        base_ind_pattern = "(?:"
        for ind in ind_list:
            base_ind_pattern += ind + "|"
        base_ind_pattern = base_ind_pattern[:-1]
        base_ind_pattern += ")"

    # ������ ����� � ������������ ��� �������������� ������� ���������������
    # � ������ �������� ������ ���������������
    base = []
    # ������ ����� � ����������� ����� ���� ��������������
    baseindentif = re.findall(r"\W" + base_ind_pattern + " +(.*?[,;)=])", text)

    # ����� ����� �� ������������� ������������
    baseindentif += re.findall(r"\W" + base_ind_pattern + " +.*?,(.*?;)", text)

    # ����� ����� � \n � �����
    baseindentif += re.findall(r"\W" + base_ind_pattern + " +([^;,)=\n]+?\n)", text)

    # ��������� ����� ��������������� �� ������ baseindentif
    for i in range(len(baseindentif)):
        base += re.findall(r"(\w+) *[,;)=\n]", baseindentif[i])

        # ��������� ���������������, � �������� � ����� [\d:\d]
        base += re.findall(r"(\w+) +\[[\d :\-*\w`]+] *[,;=\n]", baseindentif[i])

    return base


# �-� ������������ ������ ���������������, ��������� � enum
def enum_ind_search(text):
    enums = []  # ������ ��������������� ������ ����� enums � ����� �������������� ������������ enums

    # ������ ����� � ������� enums
    # � 1 ������ �������� ����� ������ �����
    # �� 2 ������ �������� �������������� enums
    enumblocks = re.findall(r"\Wenum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", text)

    # ���� ��������� enums (��������� ��������������� �� ������� enums)
    for i in range(len(enumblocks)):
        insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # ����� ������ ����� ��� ������������
        insideind = re.findall(r"(\w+) *", insideWOeq)  # ������ ��������������� ������ �����
        outsideind = re.findall(r"(\w+) *",
                                enumblocks[i][1])  # ������ ��������������� ������� ����� (������� enum)
        enumblocks[i] = (insideind + outsideind)
        enums += enumblocks[i]  # � ����� ������ ������ ���� ��������������� ��������� � ������� enum

    return enums


# ------------------------------���������������_�������----------------------------- #

# �-� �������� �� ������ allind ��������� input/output/inout ���������������
def delete_inouts(inouts, allind):
    for i in range(len(inouts)):
        if inouts[i] in allind:
            allind.remove(inouts[i])


# �-� ��������� ifdef/ifndef � �������� ������������
def preobfuscator_ifdef(file):
    # json ifdef �������
    # ����� ��� ��������� ���. ������ include
    json_file_ifdef = open("jsons/ifdefprocessing.json", "r")
    json_ifdef_struct = json.load(json_file_ifdef)

    # �������� ��� include �����
    ifdefprocessing.include_for_file(file, json_ifdef_struct)
    # ������������ ifdef/ifndef
    ifdefprocessing.ifdef_pr_forfile(file, json_ifdef_struct)

    #  ������� �����������
    erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

    # ��������� � ������ \n (����� ��� ����������� ������ ���������������)
    filetext = work_with_files.get_file_text(file)
    if filetext[0] != "\n":
        work_with_files.write_text_to_file(file, "\n" + filetext)


# �-� ���������� (������ �� ��������� ������) instance ������, ��� ���������� ��������� ���������� ������
def preobfuscator_instance(file):
    filetext = work_with_files.get_file_text(file)  # ����� �����

    modules = work_with_files.get_all_modules(os.curdir)  # ��� ������ �������

    decrypt_table = {}  # ������� ������������ ������������� ������ instance

    # ���� ������ � ���������� ������ instance
    for module in modules:

        # �����
        searched_instances = re.findall(r"\W" + module + r" +\w+ *\([\w|\W]+?\) *;", filetext)
        searched_instances += re.findall(r"\W" + module + r" *# *\([\w|\W]+?\) *\w+ *\([\w|\W]+?\);", filetext)

        # ���� �����, �� �������� ��� �����
        if searched_instances:

            # ������ ������
            for instance_block in searched_instances:
                letters_and_digits = string.ascii_letters + string.digits
                rand_string = ''.join(random.sample(letters_and_digits, 40))  # �������� ��������� ������

                # ��������� ������ � ������� ������������
                decrypt_table[rand_string] = instance_block

                # ������ � ������
                filetext = filetext.replace(instance_block, rand_string)

        # ���� �� �����, �� ���������� �����
        else:
            continue

    # ������ �������������� ������
    work_with_files.write_text_to_file(file, filetext)

    # ������� ������� ����������� ������������� ������ instance
    return decrypt_table

