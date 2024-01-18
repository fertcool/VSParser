import obfuscator
from obfuscator.deobfuscator.utilities import *
from work_with_files import *
# ------------------------------��������_�������------------------------------ #

# ������� ������������ ���� ��������������� � �����
def decryptall(file):

    filetext = get_file_text(file)  # ����� �����

    # ���� ��� ����� � ��������� ������� � �����, ����� ����� ������������ �� �� ���� ������
    ports = obfuscator.base_ind_search(filetext, ["input", "output", "inout", "parameter"])

    modules = get_modules(filetext)  # ������ �������, ��������� � ������ �����

    # �������� ������� ������������
    decrypt_table = get_decrt_in_file(file)

    # ���� ������ ��������������� �������� ������� ������������
    for ident in decrypt_table:
        filetext = re.sub(ident, decrypt_table[ident], filetext)

    # ��������������� �����, ����� �������, ��������� �� ���� ������ �������
    change_ind_allf(modules+ports)

    # ������ ������ ������ � ����
    write_text_to_file(file, filetext)


# �-� ������������ ���������� ���� ��������������� (input/output/inout, wire, reg, module, instance, parameter)
def decrypt_one_ind(file, ind):

    filetext = get_file_text(file)  # ����� �����

    decrypt_table = get_decrt_in_file(file)  # ������� ������������

    allind = []  # ������ ���� ���������������

    # ���������
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # ���� ��������� ��� �������������� - �������, �� �������� ��������������� �����
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        inouts = obfuscator.search_inouts(filetext)  # ������ ���� input/output/inout ���������������

        # ����� ���� input/output/inout ���������������
        if ind != "(?:input|output|inout)":

            # ����� ���� ����� � ���������������� ������ ind
            allind = obfuscator.base_ind_search(filetext, [ind])

            if ind == "wire":  # ��������� ��������� wire
                allind += re.findall(r"wire +struct[\w :\[\]\-`]*?\{[\w|\W]*?} *(\w+)[,;\n)=]", filetext)

            # �������� �� ������ allind ��������� input/output/inout ���������������
            obfuscator.delete_inouts(inouts, allind)

        else:

            allind = inouts

    # ���� ��������� ��� �������������� - module ��� instance, �� �������� ��������������� �����
    elif ind == "module":

        # ����� ��������������� �������
        allind = get_modules(filetext)

    elif ind == "instance":

        allind = obfuscator.search_instances(filetext)

    # ������
    else:
        print("literal not correct")
        return

    # ������ ���������� ������ ���������������
    for indef in allind:
        if indef in decrypt_table:
            filetext = re.sub(indef, decrypt_table[indef], filetext)

    # ������ ��������������� ������ � ����������� �� ���� ������
    if ind == "module" or ind == "(?:input|output|inout)" or ind == "parameter":
        change_ind_allf(allind)

    # ������ ������ ������ � ����
    write_text_to_file(file, filetext)


# �-� ������������ ��������������� input/output/inout ���������� ������
def decrypt_module_inout(file, module):

    filetext = get_file_text(file)  # ����� �����

    decrypt_table = get_decrt_in_file(file)  # ������� ������������

    # ���� ����� ������
    moduleblock = get_module_blocks(filetext, module)

    # ���� ����� ������
    if moduleblock:

        moduletext = moduleblock  # ����� ����� ������

        # ���� ����� ������
        inouts = obfuscator.search_inouts(moduletext)

        # ������ ���������� ������ ���������������
        for ind in inouts:
            if ind in decrypt_table:
                filetext = re.sub(ind, decrypt_table[ind], filetext)

        # ������ ������ ������ � ����
        write_text_to_file(file, filetext)

        # �������� ����� � ������ ������
        change_ind_allf(inouts)

    # ������
    else:
        print(module + " in " + file + " not found")
        return