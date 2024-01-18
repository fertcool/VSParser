# ������ ���������� ������ ����� ����������
# ��������� ������������ �������������� � "deobfuscator.json"

from obfuscator.deobfuscator.base_funcs import *

allfiles = get_sv_files(os.curdir)  # ��������� ����� ����� �������

# ------------------------------������_������������------------------------------ #


# ������ ������������
def launch():
    json_struct = get_json_struct(r"jsons/deobfuscator.json")

    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = get_sv_files(os.curdir)  # ��������� ����� ����� �������
    else:
        files.append(json_struct["conf"]["filename"])  # ��������� 1 ����������� ����

    # �������������� ����� ���������������� ���� �� �������� ������������
    if json_struct["tasks"]["AllDeobf"]:

        # ���� �� ���� ������
        for file in files:
            decryptall(file)

    #  �������� ������������ �������� ��� �� ���������������� ������ ��� ���������� ������
    #  ��������������� (input/output/inout, wire, reg, module, instance, parameter).
    if json_struct["tasks"]["IndDeobf"]:

        # ���� �� ���� ������
        for file in files:
            decrypt_one_ind(file, json_struct["literalclass"])

    # �������� ������������ �������� ��� �� ���������������� ������ ��� ������ ����� ������ ��������� ������
    if json_struct["tasks"]["ModuleInoutsDeobf"]:

        # ���� �� ���� ������
        for file in files:
            decrypt_module_inout(file, json_struct["module"])
