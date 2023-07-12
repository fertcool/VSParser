import json
import os
import re
from queue import Queue
import obfuscator
import scanfiles

json_file = open(r"jsons/read_hierarchy.json", "r")
json_struct = json.load(json_file)  # json �������

files = scanfiles.getsv(os.curdir)  # sv ����� ����� �������
# ifdef/ifndef ��������� ���� ������
for file in files:
    obfuscator.preobfuscator_ifdef(file)

modules = scanfiles.getallmodules(os.curdir)  # ��� ������


# ������ ������ ��������
def launch():
    # �������������� ��������� ������� �������
    if json_struct["tasks"]["a"]:
        restoring_call_structure(os.curdir)

    # ����� ������������� ����� �� ���� �������� �������
    if json_struct["tasks"]["b"]:
        search_allmodule_objects(os.curdir)

    # ���������� ������ � ����������� ��������
    if json_struct["tasks"]["c"]:
        splitting_modules_by_files(os.curdir)


# �-� ������� �������������� ��������� ������� �������
def restoring_call_structure(dir):
    inst_in_modules_dict = get_insts_in_modules(dir)  # ������� ������� (���� - �������� ������,
    # �������� - ������ instance �������� � ���� ������ (� ����� ������� � ������� �������))

    # ������ � ���� ������ ��������� ������� �������
    project_struct_report(json_struct["report_filename"], inst_in_modules_dict)

    # ������ � ���� ������ ������������� ����� ���� instance ��������
    project_objects_inst_report(json_struct["report_filename"], inst_in_modules_dict)


# �-� ��������� ������ ���� instance �������� �� ������� ������� (� ������� ������� - ��� �������)
def get_inst_list(insts_in_modules_dict):
    insts = []  # ������ instance ��������

    # ���� ���������� instance �������� �� ������� � ������
    for module in insts_in_modules_dict:
        insts += insts_in_modules_dict[module]

    return insts


# �-� �������� ������� ������� (���� - �������� ������,
# �������� - ������ instance �������� � ���� ������ (� ����� ������� � ������� �������))
def get_insts_in_modules(dir):
    insts_in_modules_dict = {}  # ������� �������

    # ���� ���������� instance �������� ������� �����
    for file in files:

        fileopen = open(file, "r")  # �������� �����
        filetext = fileopen.read()  # ����� �����
        fileopen.close()

        # ������ ������ ������� ������ ������� �����
        moduleblocks = re.findall(r"module +[\w|\W]+?endmodule", filetext)

        # ���� ������ instance �������� �� ���� ������� �����
        for moduleblock in moduleblocks:

            modulename = re.search(r"module +(\w+)", moduleblock)[1]  # ��� ������

            insts_in_modules_dict[modulename] = []  # �������������� ������ instance �������� ������

            # ���� ������ instance ������ module �� ������ modules � �����
            for module in modules:

                # �����
                searched_instance = re.findall(module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)
                searched_instance += re.findall(module + r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)

                # ���������� � ������ � ����� � ������� �������
                if searched_instance:
                    for inst in searched_instance:
                        insts_in_modules_dict[modulename].append(inst + "(" + module + ")")

                # ���� instance �������� ��� - ���������� �����
                else:
                    continue

    return insts_in_modules_dict


# �-� ������ �������� �������
def get_roots_modules(inst_in_modules_dict):
    roots = []  # �������� ������

    insts = get_inst_list(inst_in_modules_dict)  # ������ ���� instance ��������

    # ���� �������� ������� ������ �� �� �������� �� �� ��������
    for module in inst_in_modules_dict:

        # ���� ������ instance �������� ������ �� ���� - �� ��������� ���
        if inst_in_modules_dict[module]:

            # ���� - ��� �� �� instance ������ ������, �.�. ���� ������ �� ����� ����� �����������,
            # �.�. ��� ���� ��������� ������
            no_link_flag = True

            # ���������� �� ���� instance ��������, ����� ����� ���� �� 1 ������ �� ������
            for inst in insts:

                # ������ �� ������ ����, ���� ������� ������ ����� ��� ������ module
                if re.search(r"\((\w+)\)", inst)[1] == module:
                    no_link_flag = False

            # ���� ���� ��� �������, �� ��������� �������� ������
            if no_link_flag:
                roots.append(module)

    return roots


# �-� ������ ��������� ������� ������� ������� � ������ ���������������� ������ � ����
def project_struct_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # �������� �����

    fileopen.write("\n\n*------------------------------PROJECT_CALL_STRUCTURE------------------------------*\n")

    # �������� ������ �������� �������
    roots = get_roots_modules(inst_in_modules_dict)

    # �������� ������ ���� instance ��������
    insts = get_inst_list(inst_in_modules_dict)

    used = {}  # ������� ����������� � ����� instance �������� (����� �� ���� ��������� �������)
    for inst in insts:
        used[inst] = False

    modules_queue = Queue()  # ������� instance ��������

    # ������ �������� �������
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # ������ instance �������� �������� �������
    for root in roots:
        fileopen.write("ROOT: " + root + " -> " + str(inst_in_modules_dict[root]) + "\n\n")

        # ���������� instance �������� � �������� ������� � �������
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(inst)

    # ���� ������ instance �������� � ����� (���-�� ���� ������ � ������)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # ������� ������, ������ �� �������

        # ������ ������ instance �������� �������� ������
        fileopen.write(cur_module + " -> " + str(
            inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]) + "\n\n")

        # ���� ���������� instance �������� �������� ������ � �������
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

    fileopen.close()  # �������� �����


# �-� ������ � ������ � ����� ������������� ����� �� ���� instance ��������
def project_objects_inst_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # �������� �����
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")

    # �������� ������ �������� �������
    roots = get_roots_modules(inst_in_modules_dict)

    modules_queue = Queue()  # ������� instance ��������

    # ������ �������� �������
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # ������ instance �������� �������� �������
    for root in roots:
        fileopen.write("ROOT: " + root + "\n\n")

        # ���������� instance �������� � �������� ������� � �������
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root + '.' + inst)

    # ���� ������ instance �������� � ����� (���-�� ���� ������ � ������)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # ������� instance ������, ������ �� �������

        # �������� ������� instance ������ (��� ���� � ������� �������)
        fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "\n\n")

        # ���� ���������� instance �������� �������� ������ � �������
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)

    fileopen.close()  # �������� �����


# �-� ������ � ������ ������������� ����� ���� �������� (reg, net, instance, port)
def project_allobjects_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # �������� �����
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")

    # �������� ������ �������� �������
    roots = get_roots_modules(inst_in_modules_dict)

    # �������� ������� ������� �� ����� �� ��������� (reg, net, instance, port)
    modules_with_objects = scanfiles.getallmodules(os.curdir, False)

    modules_queue = Queue()  # ������� instance ��������

    # ������ �������� �������
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # ���� ������ �������� (reg, net, instance, port) �������� ������� � �����
    # � ���������� instance �������� �������� ������� � �������
    for root in roots:

        # ���� �� ���� ����� (reg, net, instance, port)
        for typeobject in modules_with_objects[root]:
            # ���� �� ���� �������� ����������� ����
            for i in range(len(modules_with_objects[root][typeobject])):
                fileopen.write(root + "." + modules_with_objects[root][typeobject][i] + " ( " + typeobject + " ) \n")

        # ���������� instance �������� �������� ������� � �������
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root + '.' + inst)

    # ���� ������ ������������� ����� ���� �������� (reg, net, instance, port)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # ������� instance ������, ������ �� �������

        # ���� ������ ������������� ����� ���� �������� (reg, net, instance, port) �������� instance �������
        for typeobject in modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]]:
            for i in range(len(modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject])):
                fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "." +
                               modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject][
                                   i] + " ( " + typeobject + " ) \n")

        # ���� ���������� instance �������� �������� ������ � �������
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)

    fileopen.close()  # �������� �����


# �-� ������� ������ ������������� ����� �� ���� �������� ������� (reg, net, instance, port)
def search_allmodule_objects(dir):

    inst_in_modules_dict = get_insts_in_modules(dir)  # ������� ������� (���� - �������� ������,
    # �������� - ������ instance �������� � ���� ������ (� ����� ������� � ������� �������))

    # ����� ������������� ����� �� ���� �������� ������� (reg, net, instance, port)
    project_allobjects_report(json_struct["report_filename"], inst_in_modules_dict)


# �-� ���������� ������ � ����������� ��������
def splitting_modules_by_files(dir):

    # ���� �� ���� ������
    for file in files:

        fileopen = open(file, "r")  # �������� �����
        filetext = fileopen.read()  # ����� �����
        fileopen.close()

        # ������ ������ ������� ������ ������� �����
        moduleblocks = re.findall(r"module +[\w|\W]+?endmodule", filetext)

        # ���� ����� ���� � ����� ��� 1 �������, �� ��������� ����
        if len(moduleblocks) > 1:

            # ���� ��������� ������� ������ � �����
            for moduleblock in moduleblocks:

                modulename = re.search(r"module +(\w+)", moduleblock)[1]  # ��� ������

                filetext_with_cur_module = filetext  # ����� ����� � ������� �������

                # ���� �������� �� ������ ����� ������ �������
                for moduleblock_another in moduleblocks:
                    if moduleblock_another == moduleblock:
                        continue
                    else:
                        filetext_with_cur_module = filetext_with_cur_module.replace(moduleblock_another, '')

                # ������� ����� ���� � ��������� ������� � ��������� ���� �������� ��� ����� � ����� ������
                newfileopen = open(re.sub(r"[\w\.]+$", modulename, file) + ".sv", "w")
                newfileopen.write(filetext_with_cur_module)
                newfileopen.close()

            # ������� ���� � ����������� ��������
            os.remove(file)
