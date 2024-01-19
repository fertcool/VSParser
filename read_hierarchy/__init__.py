# ������ ������ �������� �������
# ��������� ������������ �������������� � "read_hierarchy.json"
import obfuscator
from read_hierarchy.base_funcs import *

# ------------------------------�����������_����������_����������------------------------------ #

json_struct = get_json_struct(r"jsons/read_hierarchy.json")
files = []  # sv ����� ����� �������
modules = []  # ��� ������


# ------------------------------������_������_��������------------------------------ #

# ������ ������ ��������
def launch():
    global files, modules
    # ������������� ���������� ����������
    files = get_sv_files(os.curdir)  # sv ����� ����� �������

    # ifdef/ifndef ��������� ���� ������
    for file_g in files:
        obfuscator.preobfuscator_ifdef(file_g)

    modules = get_all_modules()  # ��� ������

    # �������������� ��������� ������� �������
    if json_struct["tasks"]["CallStructure"]:
        restoring_call_structure()

    # ����� ������������� ����� �� ���� �������� �������
    if json_struct["tasks"]["AllObjects"]:
        search_allmodule_objects()

    # ���������� ������ � ����������� ��������
    if json_struct["tasks"]["SplittingModules"]:
        splitting_modules_by_files()