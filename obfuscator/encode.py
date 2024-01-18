import random
import string
from work_with_files import *

# ------------------------------�������_����������------------------------------ #


# �-� ���������� ��������������� � ������
def encrypt_text(allind, filetext, decrypt_table):
    # ���� ������ ���� ���������������
    for ind in allind:
        randlength = random.randint(8, 32)  # ����� ��������� ����� ������
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, randlength))  # ��������� ��������� ������

        decrypt_table[rand_string] = ind  # ��������� � ������� ����� ������������ ������ ��������������

        # ������ � ����� ������ ��������������
        filetext = change_ind(filetext, ind, rand_string)

    return filetext


# �-� ������ ������ ������ "text" �������������� ������ � ���� "file"
def encrypt_file(allind, file, text, decrypt_table):
    filetext = get_file_text(file)  # ����� �����

    # �������� �� ������������� �����
    filetext = filetext.replace(text, encrypt_text(allind, text, decrypt_table))

    # ���������� ���
    write_text_to_file(file, filetext)


# �-� �������� (��� ���������� � ������������ ����) ������� ������ ���������������
def write_decrt_in_file(file, decrypt_table):
    if decrypt_table:
        add_text_to_file(str(decrypt_table), file.replace(".sv", "_decrypt_table.txt"))


# �-� ������ ��������������� � ������ �� �����
def change_ind(text, ind, newind):
    indefic = set(re.findall(r'\W' + ind + r'\W', text))  # ����� ���� ���������� � ������� ���������������
    # ���� ������ ���������� � ������������ ��������� ��
    # �����
    # ���� ������ ������� ���������� �� ��������� ������
    for indef in indefic:
        first = indef[0]  # ����������� ������ ����� �� ����������
        last = indef[-1]  # ����������� ������ �� ����������

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