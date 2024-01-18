import random
import string

import erase_comments
import ifdefprocessing
from obfuscator.search_inds import search_instance_blocks
from work_with_files import *


# ------------------------------���������������_�������----------------------------- #

# �-� �������� �� ������ allind ��������� input/output/inout ���������������
def delete_inouts(inouts, allind):
    for i in range(len(inouts)):
        if inouts[i] in allind:
            allind.remove(inouts[i])


# �-� ��������� ifdef/ifndef � �������� ������������
def preobfuscator_ifdef(file):

    # �������� ��� include �����
    ifdefprocessing.include_for_file(file)
    # ������������ ifdef/ifndef
    ifdefprocessing.ifdef_pr_forfile(file)

    #  ������� �����������
    erase_comments.delete(file, ["/\*[\s|\S]*?\*/", "//[^\n]*\n"], False)

    # ��������� � ������ \n (����� ��� ����������� ������ ���������������)
    filetext = get_file_text(file)
    if filetext[0] != "\n":
        write_text_to_file(file, "\n" + filetext)


# �-� ���������� (������ �� ��������� ������) instance ������, ��� ���������� ��������� ���������� ������
def preobfuscator_instance(file):
    filetext = get_file_text(file)  # ����� �����

    # modules = get_all_modules()  # ��� ������ �������

    decrypt_table = {}  # ������� ������������ ������������� ������ instance

    searched_instances = search_instance_blocks(filetext)

    for inst_block in searched_instances:
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, 40))  # �������� ��������� ������

        # ��������� ������ � ������� ������������
        decrypt_table[rand_string] = inst_block

        # ������ � ������
        filetext = filetext.replace(inst_block, rand_string)

    # ������ �������������� ������
    write_text_to_file(file, filetext)

    # ������� ������� ����������� ������������� ������ instance
    return decrypt_table

