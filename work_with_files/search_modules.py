import os
import re

from work_with_files.file_work import get_file_text
from work_with_files.search_sv import get_sv_files

# ------------------------------�������_������_�������------------------------------ #

# �-� ������ ������ ���� ������� ������� ��� �� ������� ������� (� ��������� reg, net, instance, port)
def get_all_modules(onlymodules = True):
    # onlymodules - ���� ������ �� ������� ��� ��������
    # ����� ������� ���������� ������� ��� ����������� � ��������� ��������� ifdef/ifndef
    # ����� ������������ obfuscator.preobfuscator()

    svfiles = get_sv_files(os.curdir)  # ������ ����� sv ������

    # ���� ���� onlymodules = false �� �������� �� ��������
    if not onlymodules:

        modules = {}  # ������� ������� �� ���� �������, ��� ���� - �������� ������,
        # � �������� - ������� ����� reg, net, instance, port �� �������� ��������������� ��������

    # ���� ���� onlymodules = true �� �������� �� �������
    else:
        modules = []  # ������ ������� �� ���� �������

    # ����� ������� �� ���� ������
    for svfile in svfiles:
        filetext = get_file_text(svfile)
        if not onlymodules:
            modules.update(get_modules(filetext, onlymodules))
        else:
            modules += get_modules(filetext, onlymodules)

    return modules


# �-� ������ ���� ������� ������� ���� ������ ������� � ������
def get_modules(text, onlymodules=True):
    import obfuscator
    # ���� ���� onlymodules = false �� �������� �� ��������
    if not onlymodules:

        modules = {}  # ������� ������� �� ���� �������, ��� ���� - �������� ������,
        # � �������� - ������� ����� reg, net, instance, port �� �������� ��������������� ��������

    # ���� ���� onlymodules = true �� �������� �� �������
    else:
        modules = []  # ������ ������� �� ���� �������

    # ������ ������ ������� ������ ������� �����
    moduleblocks = get_module_blocks(text)

    # ���� ��������� ���� �������
    for moduleblock in moduleblocks:

        modulename = re.search(r"module +(\w+)", moduleblock)[1]  # ��� ������

        # ���� ������������ ������� �������
        if not onlymodules:

            inouts = obfuscator.search_inouts(moduleblock)  # ������ ������ ������

            instances = obfuscator.search_instances(moduleblock)  # ������ instance �������� ������

            nets_strs = re.findall(
                r"(?:wire|tri|tri0|tri1|supply0|"  # ������ ����� ��������� nets
                r"supply1|trireg|wor|triand|"
                r"trior|wand) +([\w :\[\]\-`]*?[,;\n)=])", moduleblock)

            nets_strs += re.findall(r"(?:wire|tri|tri0|tri1|supply0|"  # ������ ����� � ����������� �������� nets
                                    r"supply1|trireg|wor|triand|"
                                    r"trior|wand) +struct[\w :\[\]\-`]*?\{[\w|\W]*?} *(\w+)[,;\n)=]", moduleblock)

            nets = []  # �������� ������ � nets ���������

            # ��������� ����� ��������������� �� ������ nets
            for i in range(len(nets_strs)):
                nets += re.findall(r"(\w+) *[,;\n)=]", nets_strs[i])

                # ��������� ���������������, � ������� � ����� [\d:\d]
                nets += re.findall(r"(\w+) +\[[\d :\-*\w`]+] *[,;=\n]", nets_strs[i])

            regs = obfuscator.base_ind_search(moduleblock, ["reg"])

            allind = set(inouts + regs + nets + instances)  # ������ ���� ���������������

            # �������� �� ������ allind ��������� input/output/inout ���������������
            obfuscator.delete_inouts(inouts, allind)

            # ���������� �������� reg, net, instance, port � �������
            modules[modulename] = {}
            modules[modulename]["port"] = inouts
            modules[modulename]["net"] = nets
            modules[modulename]["regs"] = regs
            modules[modulename]["instances"] = instances

        # ���� ������������ ������ �������
        else:

            # ��������� ������ � ������
            modules.append(modulename)

    return modules


# �-� ������������ ����� ������ ������� ��� ����� ����������� ������
def get_module_blocks(text, modulename = None):

    if modulename:
        module_block = re.search(r"\Wmodule +" + modulename + r"[\w|\W]+?endmodule", text)
        if module_block:
            return module_block[0]
        else:
            return []
    else:
        return re.findall(r"\Wmodule +[\w|\W]+?endmodule", text)
