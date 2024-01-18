
from read_hierarchy.search_report import *

# ------------------------------��������_�������------------------------------ #

# �-� ������� �������������� ��������� ������� �������
def restoring_call_structure():
    from read_hierarchy import json_struct
    inst_in_modules_dict = get_insts_in_modules()  # ������� ������� (���� - �������� ������,
    # �������� - ������ instance �������� � ���� ������ (� ����� ������� � ������� �������))

    # ������ � ���� ������ ��������� ������� �������
    project_struct_report(json_struct["report_filename"], inst_in_modules_dict)

    # ������ � ���� ������ ������������� ����� ���� instance ��������
    project_objects_inst_report(json_struct["report_filename"], inst_in_modules_dict)


# �-� ������� ������ ������������� ����� �� ���� �������� ������� (reg, net, instance, port)
def search_allmodule_objects():
    from read_hierarchy import json_struct
    inst_in_modules_dict = get_insts_in_modules()  # ������� ������� (���� - �������� ������,
    # �������� - ������ instance �������� � ���� ������ (� ����� ������� � ������� �������))

    # ����� ������������� ����� �� ���� �������� ������� (reg, net, instance, port)
    project_allobjects_report(json_struct["report_filename"], inst_in_modules_dict)


# �-� ���������� ������ � ����������� ��������
def splitting_modules_by_files():
    from read_hierarchy import files
    # ���� �� ���� ������
    for file in files:

        filetext = get_file_text(file)  # ����� �����

        # ������� ������ ����� endmodule (����� ���� ����� �� ��������� � ������� ������)
        filetext = re.sub(r"endmodule *: *\w+", r"endmodule", filetext)

        # ������ ������ ������� ������ ������� �����
        moduleblocks = get_module_blocks(filetext)

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

                # ������� ������ �������
                filetext_with_cur_module = delete_indents(filetext_with_cur_module)

                # ������� ����� ���� � ��������� ������� � ��������� ���� �������� ��� ����� � ����� ������
                write_text_to_file(re.sub(r"[\w\.]+$", modulename, file) + ".sv",
                                                   filetext_with_cur_module)

            # ������� ���� � ����������� ��������
            os.remove(file)