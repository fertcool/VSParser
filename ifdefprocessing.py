import json
import os
import re
import scanfiles
import erase_comments

# �-� ����������� ������������� sv ������
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


    if json_struct["tasks"]["b"]:
        # ���� �� ���� ������
        for file in files:

            #  ������� ����������� � �������������
            erase_comments.delete(file, [r"/\* *`define *[\s|\S]*?\*/", r"// *`define *[^\n]*\n"], False)

            fileopen = open(file, "r")  # �������� �����
            filestr = fileopen.read()

            # ���� ���� ���� ����� ifdef ��� ifndef � �����
            while(re.search(r"`(?:ifndef|ifdef)[\s|\S]*?`endif", filestr)):

                # ����� ���� ������ ifdef/ifndef (�������� � ����������)
                ifdefs = re.findall(r"`(?:ifndef|ifdef)[\s|\S]*?`endif", filestr)

                # ������� ��������, ���� ��� ���� (�������� ifdef...ifdef...endif -> ifdef...endif)
                for i in range(len(ifdefs)):
                    ifs = re.findall(r"`(?:ifndef|ifdef) +\w+", ifdefs[i])
                    if len(ifs)>1:
                        ifdefs[i] = re.search(r"[\s|\S]"+ifs[len(ifs)-1]+r"[\s|\S]*?`endif", ifdefs[i])[0]
                        ifdefs[i] = ifdefs[i][1:]

                # ���� �� ������� �����
                for ifdef in ifdefs:

                    index = filestr.find(ifdef)
                    textbefore = filestr[:index]  # ����� �� �����

                    defines = re.findall(r"`define +\w+\n", textbefore)  # ��� define �� �����

                    # ��������� ������ �������� define
                    for i in range(len(defines)):
                        defines[i] = re.sub("`define +", '', defines[i])
                        defines[i] = re.sub("\n", '', defines[i])

                    # # �������� ���� �� ������������������ define � defines
                    # # �������������� ������� ��
                    # for define in defines:
                    #     for definecom in defineswithcom:
                    #         if define in definecom:
                    #             defines.remove(define)

                    # ��������� �����
                    newifdef = ifblockprocessing(ifdef, defines)

                    filestr = filestr.replace(ifdef, newifdef)

            # ������ � ���� ���� ��� ������ ������ ifdef/ifndef
            fileopen.close()
            fileopen = open(file, "w")

            fileopen.write(filestr)
            fileopen.close()

# �-� ����������� 1 ���� ifdef/ifndef
def ifblockprocessing(blockstr, defines):

    # ������ �������� �������� �����
    ifdef = re.search(r"`(?:ifndef|ifdef) +\w+\n", blockstr)[0]
    elsifs = re.findall(r"`elsif +\w+\n", blockstr)
    else_ = re.search(r"`else", blockstr)

    if else_ != None:
        else_ = else_[0]

    # ���������� ������� ifdef/ifndef � define
    for define in defines:
        if define in ifdef:
            # ���� ����� ���������� � define � �� ������������ ifdef, �� ���������� ��� �����
            if "ifdef" in ifdef:
                blockstr = cleanblock(blockstr, ifdef)
                return blockstr
            # ���� ����� ���������� � define � �� ������������ ifndef
            else:
                return ""  # ��������� ������� (�.�. ���� ifndef ��������)

    # ���� ���������� � define �� ���� ������� � �� ������������ ifndef, ��
    # ��������� ��� �����
    if "ifndef" in ifdef:
        blockstr = cleanblock(blockstr, ifdef)
        return blockstr

    # ���������� elsif � define
    for define in defines:
        for elsif in elsifs:
            if define in elsif:
                # ���� ����� ����������, �� ���������� ��� ����� elsif
                blockstr = cleanblock(blockstr, elsif)
                return blockstr

    # ������ ���� � else
    if else_:
        blockstr = cleanblock(blockstr, else_)
        return blockstr

    # ���� �� ����� ������� ����������, ���������� �������
    return ""

# �-� ������������ ���������� ��� �����
def cleanblock(block, face):
    blockwithface = re.search(face + r"[\s|\S]*?`elsif", block)
    if blockwithface != None:  # ���� ���� � elsif ������
        blockwithface = blockwithface[0]
        blockwithface = re.sub(face, '', blockwithface)
        blockwithface = re.sub("`elsif", '', blockwithface)
    else:
        blockwithface = re.search(face + r"[\s|\S]*?`else", block)
        if blockwithface != None:  # ���� ���� � else ������
            blockwithface = blockwithface[0]
            blockwithface = re.sub(face, '', blockwithface)
            blockwithface = re.sub("`else", '', blockwithface)
        else: # ���� ���� � endif ������
            blockwithface = re.search(face + r"[\s|\S]*?`endif", block)
            blockwithface = blockwithface[0]
            blockwithface = re.sub(face, '', blockwithface)
            blockwithface = re.sub("`endif", '', blockwithface)

    return blockwithface

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
            else:  # ���� ���� ��� �������
                filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                 filestr)
            continue

    return filestr

