from work_with_files import *

# ------------------------------�������_������_�_INCLUDE_�������------------------------------ #


# �-� ����������� � ����� sv ����� include ����� (� ��� ����� ������� include ����������� �����)
def addincludes(filetext, included = None):
    from ifdefprocessing import json_struct
    if included is None:
        included = []

    # ����� ���� include � ����� (������������� ���������������)
    includes = re.findall(r"`include *\"([\w\.]+)\"", filetext)

    # ���� �� ���� ���������� ������
    for include in includes:
        existfile = False  # ���� ������������� ����������� �����

        # ���� �� ���� �����������, ��� ������ �������� include �����
        for includepath in json_struct["includes"]:

            # ���� ���� � ������� ��������� ���� (� �� ��� �� ��� �������)
            # , �� ��������� ����� ����������� �����
            if os.path.exists(os.path.join(includepath, include)) and include not in included:

                existfile = True  # ���� ������������� �����

                includetext = get_file_text(os.path.join(includepath, include))  # ����� ����������� �����

                # ��������� � ���� �� ����� 1 ���������
                filetext = re.sub("`include *\""+include+"\"", includetext, filetext, 1)

                # �������� ������������� ���������
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                  filetext)

                # ��������� ����������� ���� � ������ ����������
                included.append(include)

                # ������ ������������� ���� (���� ����� ���������)
                filetext = addincludes(filetext, included)

                # �������, �.�. ��� ����� � �������� ����
                break

        # ���� ���������� ���� �� ��� ������, �� ��������� ��������������� ������� � ���� � ���������� �����
        if not existfile:

            # ��������� �������
            if include not in included:  # ���� ���� �� ��� �������
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file don't exist",
                                  filetext)
            else:  # ���� ���� ��� �������
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                  filetext)
            continue

    return filetext


# �-� ���������� ���� include ������ ��� 1 �����
def include_for_file(file):

    filetext = get_file_text(file)  # ����� �����

    # �������� ����� sv ����� - �������� `include �� ����� ���������������� �����
    filetext = addincludes(filetext)

    write_text_to_file(file, filetext)  # ������ ������ ������ � ����