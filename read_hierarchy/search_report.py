from queue import Queue
from read_hierarchy.utilities import *

# ------------------------------�������_������_�_������_��������------------------------------ #

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
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

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
    modules_with_objects = get_all_modules(False)

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