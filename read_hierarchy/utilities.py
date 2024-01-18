from work_with_files import *

# ------------------------------���������������_�������------------------------------ #

# �-� ��������� ������ ���� instance �������� �� ������� ������� (� ������� ������� - ��� �������)
def get_inst_list(insts_in_modules_dict):

    insts = []  # ������ instance ��������

    # ���� ���������� instance �������� �� ������� � ������
    for module in insts_in_modules_dict:
        insts += insts_in_modules_dict[module]

    return insts


# �-� �������� ������� ������� (���� - �������� ������,
# �������� - ������ instance �������� � ���� ������ (� ����� ������� � ������� �������))
def get_insts_in_modules():
    from read_hierarchy import files, modules

    insts_in_modules_dict = {}  # ������� �������

    # ���� ���������� instance �������� ������� �����
    for file in files:

        filetext = get_file_text(file)  # ����� �����

        # ������ ������ ������� ������ ������� �����
        moduleblocks = get_module_blocks(filetext)

        # ���� ������ instance �������� �� ���� ������� �����
        for moduleblock in moduleblocks:

            modulename = re.search(r"module +(\w+)", moduleblock)[1]  # ��� ������

            insts_in_modules_dict[modulename] = []  # �������������� ������ instance �������� ������

            # ���� ������ instance ������ module �� ������ modules � �����
            for module in modules:

                # �����
                searched_instance = re.findall(r"(?<!module)[ \n]+" + module + r"[ \n]+(\w+)[ \n]*\([\w|\W]*?\) *;", moduleblock)
                searched_instance += re.findall(r"(?<!module)[ \n]+" + module + r"[ \n]+#\([\w|\W]*?\)[ \n]*(\w+)[ \n]*\([\w|\W]*?\) *;", moduleblock)

                # ���������� � ������ � ����� � ������� �������
                if searched_instance:
                    for inst in searched_instance:
                        insts_in_modules_dict[modulename].append(inst + "(" + module + ")")

                # ���� instance �������� ��� - ���������� �����
                else:
                    continue

    return insts_in_modules_dict