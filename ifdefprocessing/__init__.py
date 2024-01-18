# ������ ������ � IFDEF/IFNDEF ������� � ��������� INCLUDE ������
# ��������� ������������ �������������� � "ifdefprocessing.json"
# ����� ifdef ���������� ��������� ����������� � define


from ifdefprocessing.idef import ifdef_pr_forfile
from ifdefprocessing.include import include_for_file
from work_with_files import *

json_struct = get_json_struct(r"jsons/ifdefprocessing.json")
# ------------------------------������_�������------------------------------ #

# �-� ����������� ������������� sv ������
def launch():

    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = get_sv_files(os.curdir)  # ��������� ����� ����� �������
    else:
        files.append(json_struct["conf"]["filename"])  # ��������� 1 ����������� ����

    # ���������� include ������
    if json_struct["tasks"]["IncludePr"]:

        # ���� �� ���� ������
        for file in files:
            include_for_file(file)

    # ��������� ifdef/ifndef
    if json_struct["tasks"]["IfdefPr"]:

        # ���� �� ���� ������
        for file in files:
            ifdef_pr_forfile(file)