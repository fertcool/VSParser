import ast
from work_with_files import *

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
        return {}


# �-� ���������� ��������� ��������������� �� ���� ������ �������
def change_ind_allf(identifiers):
    from obfuscator.deobfuscator import allfiles
    for file in allfiles:

        filetext = get_file_text(file)  # ����� �����

        decrypt_table = get_decrt_in_file(file)

        if decrypt_table:

            for ind in identifiers:
                if ind in decrypt_table:
                    filetext = filetext.replace(ind, decrypt_table[ind])

            # ������ ����������� ������ � ����
            write_text_to_file(file, filetext)
        else:
            continue
