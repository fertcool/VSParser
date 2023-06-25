import json
import os
import re
import scanfiles

#�-� ����������� ������������� sv ������
def launch():
    json_file = open(r"ifdefprocessing.json", "r")
    json_struct = json.load(json_file)

    files = []  # ������ ������ ��� ������� ���������� ������
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.getsv(os.curdir)  # ��������� ����� ����� �������
    else:
        files.append(json_struct["conf"]["filename"])  # ��������� 1 ����������� ����

    # ���������� include ������
    if json_struct["tasks"]["a"]:

        # ���� �� ���� ������
        for file in files:
            fileopen = open(file, "r")  # �������� �����
            filestr = fileopen.read()

            # �������� ����� sv ����� - �������� `include �� ����� ���������������� �����
            filestr = addincludes(json_struct, filestr)

            fileopen.close()  # �������� �����
            fileopen = open(file, "w")
            fileopen.write(filestr)  # ������ ������ ������ � ����


# �-� ����������� � ����� sv ����� include ����� (� ��� ����� ������� include ����������� �����)
def addincludes(json, filestr, included = None):

    if included is None:
        included = []

    # ����� ���� include � ����� (������������� ���������������)
    includes = re.findall(r"`include *\"[\w\.]+\"", filestr)

    # ��������� ������ �������� ���������� ������
    for i in range(len(includes)):
        includes[i] = re.sub("`include +", '', includes[i])
        includes[i] = re.sub("\"", '', includes[i])

    # ���� �� ���� ���������� ������
    for include in includes:
        existfile = False  # ���� ������������� ����������� �����

        # ���� �� ���� �����������, ��� ������ �������� include �����
        for includepath in json["includes"]:

            # ���� ���� � ������� ��������� ���� (� �� ��� �� ��� �������)
            # , �� ��������� ����� ����������� �����
            if os.path.exists(includepath+"\\"+include) and include not in included:
                existfile = True
                includetextopen = open(includepath+"\\"+include, "r")
                includetext = includetextopen.read()

                # ��������� � ���� �� ����� 1 ���������
                filestr = re.sub("`include *\""+include+"\"", includetext, filestr, 1)

                # �������� ������������� ���������
                filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                 filestr)
                includetextopen.close()

                # ��������� ����������� ���� � ������ ����������
                included.append(include)

                # ������ ������������� ���� (���� ����� ���������)
                filestr = addincludes(json, filestr, included)

                # �������, �.�. ��� ����� � �������� ����
                break

        # ���� ���������� ���� �� ��� ������, �� ��������� ��������������� ������� � ���� � ���������� �����
        if not existfile:

            # ��������� �������
            if include not in included: # ���� ���� �� ��� �������
                filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file don't exist", filestr)
            else: # ���� ���� ��� �������
                filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                 filestr)
            continue

    return filestr

