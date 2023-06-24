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
def addincludes(json, filestr, included = []):

    # ����� ���� include � ����� (������ ��� ��������)
    includes = list(set(re.findall(r"`include *\"[\w\.]+\"", filestr)))

    # ��������� ������ �������� ���������� ������
    for i in range(len(includes)):
        includes[i] = re.sub("`include +", '', includes[i])
        includes[i] = re.sub("\"", '', includes[i])

    # ���� �� ���� ���������� ������
    for include in includes:
        existfile = False  # ���� ������������� ����������� �����

        # ���� �� ���� �����������, ��� ������ �������� include �����
        for includepath in json["includes"]:

            # ���� ���� � ������� ��������� ����, �� ��������� ����� ����������� �����
            if os.path.exists(includepath+"\\"+include) and include not in included:
                existfile = True
                includetextopen = open(includepath+"\\"+include, "r")
                includetext = includetextopen.read()
                filestr = re.sub("`include *\""+include+"\"", includetext, filestr, 1)

                # �������� ������������� ���������
                filestr = re.sub("`include *\"" + include + "\"", '', filestr)
                includetextopen.close()

                included.append(include)
                print(include)
                # includetextopen = open(includepath + "\\" + include, "w")
                # includetextopen.write(filestr)
                # includetextopen.close()
                break

        # ���� ���������� ���� �� ��� ������, �� ��������� ��������������� ������� � ���� � ���������� �����
        if not existfile:

            # ��������� �������
            filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" //file don't exist", filestr)

            # ������� ���������� ���� �� ������
            includes.remove(include)
            continue

    # ���� ������ 1 ���� ��� ��������, �������� � ��� �����
    if len(includes) != 0:
        filestr = addincludes(json, filestr, included)

    return filestr

