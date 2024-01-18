
from work_with_files import *
# ------------------------------�������_������_���������������----------------------------- #

# ��������� ����� ���� instance ��������
def search_instances(text):

    # ��� ������ � �� �����
    modules = get_all_modules()

    instances = []  # ������ instance ��������

    # ���� ������ instance ������ module �� ������ modules � �����
    for module in modules:

        # �����
        searched_instance = re.findall(r"(?<!module)[ \n]+" + module + r"[ \n]+(\w+)[ \n]*\([\w|\W]*?\) *;", text)
        searched_instance += re.findall(
            r"(?<!module)[ \n]+" + module + r"[ \n]+#\([\w|\W]*?\)[ \n]*(\w+)[ \n]*\([\w|\W]*?\) *;", text)

        # ���������� � ������
        if searched_instance:
            instances += searched_instance
        else:
            continue

    # ������� ������ ���� instance
    return instances


# ��������� ����� ������� ���� instance ��������
def search_instance_blocks(text):

    # ��� ������
    modules = get_all_modules()

    instance_blocks = []  # ������ instance ��������

    # ���� ������ instance ������ module �� ������ modules � �����
    for module in modules:

        # �����
        searched_instance = re.findall(r"(?<!module)[ \n]+(" + module + r"[ \n]+\w+[ \n]*\([\w|\W]*?\) *;)", text)
        searched_instance += re.findall(
            r"(?<!module)[ \n]+(" + module + r"[ \n]+#\([\w|\W]*?\)[ \n]*\w+[ \n]*\([\w|\W]*?\) *;)", text)

        # ���������� � ������
        if searched_instance:
            instance_blocks += searched_instance
        else:
            continue

    # ������� ������ ���� instance
    return instance_blocks


# �-� ������ ������ input/output/inout � ������
def search_inouts(text):
    inouts = base_ind_search(text, ["(?:input|output|inout)"])  # ������ input/output/inout ������

    return inouts


# �-� ������������ ������ ������� �������� (��� ��������) ��������������� � ������
def base_ind_search(text, ind_list):
    base_ind_pattern = ind_list[0]

    # ������ ����������� ��������� ��� ���������� ������ ������ �� ���������������
    if len(ind_list) > 1:
        base_ind_pattern = "(?:"
        for ind in ind_list:
            base_ind_pattern += ind + "|"
        base_ind_pattern = base_ind_pattern[:-1]
        base_ind_pattern += ")"

    # ������ ����� � ������������ ��� �������������� ������� ���������������
    # � ������ �������� ������ ���������������
    base = []
    # ������ ����� � ����������� ����� ���� ��������������
    baseindentif = re.findall(r"\W" + base_ind_pattern + " +(.*?[,;)=])", text)

    # ����� ����� �� ������������� ������������
    baseindentif += re.findall(r"\W" + base_ind_pattern + " +.*?,(.*?;)", text)

    # ����� ����� � \n � �����
    baseindentif += re.findall(r"\W" + base_ind_pattern + " +([^;,)=\n]+?\n)", text)

    # ��������� ����� ��������������� �� ������ baseindentif
    for i in range(len(baseindentif)):
        base += re.findall(r"(\w+) *[,;)=\n]", baseindentif[i])

        # ��������� ���������������, � �������� � ����� [\d:\d]
        base += re.findall(r"(\w+) +\[[\d :\-*\w`]+] *[,;=\n]", baseindentif[i])

    return base


# �-� ������������ ������ ���������������, ��������� � enum
def enum_ind_search(text):
    enums = []  # ������ ��������������� ������ ����� enums � ����� �������������� ������������ enums

    # ������ ����� � ������� enums
    # � 1 ������ �������� ����� ������ �����
    # �� 2 ������ �������� �������������� enums
    enumblocks = re.findall(r"\Wenum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", text)

    # ���� ��������� enums (��������� ��������������� �� ������� enums)
    for i in range(len(enumblocks)):
        insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # ����� ������ ����� ��� ������������
        insideind = re.findall(r"(\w+) *", insideWOeq)  # ������ ��������������� ������ �����
        outsideind = re.findall(r"(\w+) *",
                                enumblocks[i][1])  # ������ ��������������� ������� ����� (������� enum)
        enumblocks[i] = (insideind + outsideind)
        enums += enumblocks[i]  # � ����� ������ ������ ���� ��������������� ��������� � ������� enum

    return enums