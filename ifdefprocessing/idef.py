import erase_comments
from work_with_files import *

# ------------------------------�������_IFDEF/IFNDEF_���������------------------------------ #


# �-� ifdef/ifndef ��������� �����
def ifdef_pr_forfile(file):
    from ifdefprocessing import json_struct
    #  ������� ����������� � �������������
    erase_comments.delete(file, [r"/\* *`define *[\s|\S]*?\*/", r"// *`define *[^\n]*\n"], False)

    filetext = get_file_text(file)  # ����� �����

    # ���� ���� ���� ����� ifdef ��� ifndef � �����
    while (re.search(r"`(?:ifndef|ifdef)[\s|\S]*?`endif", filetext)):

        # ����� ���� ������ ifdef/ifndef (�������� � ����������)
        ifdefs = re.findall(r"`(?:ifndef|ifdef)[\s|\S]*?`endif", filetext)

        # ������� ��������, ���� ��� ���� (�������� ifdef...ifdef...endif -> ifdef...endif)
        for i in range(len(ifdefs)):
            ifs = re.findall(r"`(?:ifndef|ifdef) +\w+", ifdefs[i])
            if len(ifs) > 1:
                ifdefs[i] = re.search(r"[\s|\S]" + ifs[len(ifs) - 1] + r"[\s|\S]*?`endif", ifdefs[i])[0]
                ifdefs[i] = ifdefs[i][1:]

        # ���� ��������� ������� �����
        for ifdef in ifdefs:

            index = filetext.find(ifdef)
            textbefore = filetext[:index]  # ����� �� �����

            defines = re.findall(r"`define +\w+", textbefore)  # ��� define �� �����
            defines.extend(json_struct["defines"])  # ��������� ������� define
            # ��������� ������ �������� define
            for i in range(len(defines)):
                defines[i] = re.sub("`define +", '', defines[i])
                defines[i] = re.sub("\n", '', defines[i])

            # ��������� �����
            newifdef = ifblockprocessing(ifdef, defines)

            # ���������� ������������ ����� � ����
            filetext = filetext.replace(ifdef, newifdef)

    # ������� ������ �������
    filetext = delete_indents(filetext)

    # ������ � ���� ���� ��� ������ ������ ifdef/ifndef
    write_text_to_file(file, filetext)


# �-� ����������� 1 ���� ifdef/ifndef
def ifblockprocessing(blockstr, defines):

    # ������ �������� �������� �����
    ifdef = re.search(r"`(?:ifndef|ifdef) +\w+\n", blockstr)[0]
    elsifs = re.findall(r"`elsif +\w+\n", blockstr)
    else_ = re.search(r"`else", blockstr)

    if else_:
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

    if blockwithface:  # ���� ���� � elsif ������
        blockwithface = blockwithface[0]
        blockwithface = re.sub(face, '', blockwithface)
        blockwithface = re.sub("`elsif", '', blockwithface)
    else:

        blockwithface = re.search(face + r"[\s|\S]*?`else", block)

        if blockwithface:  # ���� ���� � else ������
            blockwithface = blockwithface[0]
            blockwithface = re.sub(face, '', blockwithface)
            blockwithface = re.sub("`else", '', blockwithface)

        else:  # ���� ���� � endif ������
            blockwithface = re.search(face + r"[\s|\S]*?`endif", block)
            blockwithface = blockwithface[0]
            blockwithface = re.sub(face, '', blockwithface)
            blockwithface = re.sub("`endif", '', blockwithface)

    return blockwithface