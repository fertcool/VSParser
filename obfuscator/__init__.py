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
# ����� ����������� ���������� include-ifdef ��������� � �������� ������������
# ���������� �� ������������ ��� �������� instance �������� ����� "."
# ���� ������������� ������ ��� �� �����, ���������, �� ��� ���������� � � instance ����������� �������


from obfuscator.base_funcs import *

json_struct = get_json_struct(r"jsons/obfuscator.json")

# ------------------------------������_����������------------------------------ #


def launch():
    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = get_sv_files(os.curdir)  # ��������� ����� ����� �������
    else:
        files.append(json_struct["conf"]["filename"])  # ��������� 1 ����������� ����

    # ���������� �� ���� ���������������
    if json_struct["tasks"]["AllObf"]:

        # ���� �� ���� ������
        for file in files:
            allind_search_and_replace(file)

    # ���������� �� ���������� ������ ��������������� (input/output/inout, wire, reg, module, instance, parameter)
    if json_struct["tasks"]["IndObf"]:

        # ���� �� ���� ������
        for file in files:
            ind_search_and_replace(file, json_struct["literalclass"])

    # ���������� �� ��������������� input/output/inout � �������� ������
    if json_struct["tasks"]["ModuleWoInoutsObf"]:

        # ���� �� ���� ������
        for file in files:
            module_search_and_replace_wo_inout(file, json_struct["module"])

    # ���������� � ������ (protect on - protect off)
    if json_struct["tasks"]["ProtectObf"]:

        # ���� �� ���� ������
        for file in files:
            ind_search_and_replace_protect(file)