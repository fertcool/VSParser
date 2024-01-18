
from obfuscator.encode import encrypt_file, write_decrt_in_file, encrypt_text, regexp_to_str
from obfuscator.search_inds import search_instances, search_inouts, base_ind_search, enum_ind_search
from obfuscator.utilities import *


# ------------------------------��������_�������------------------------------ #

# �-� ���������� ������ � �������� `pragma protect on - `pragma protect off
def ind_search_and_replace_protect(file):

    filetext = get_file_text(file)  # ����� �����

    # ����� ��������������� ����� ����
    protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

    if protectblocks:
        # ��������� ifdef/ifndef
        preobfuscator_ifdef(file)

        filetext = get_file_text(file)  # ����� ����� ����� ����� ��������� ifdef/ifndef

        # ��������� �����, �.�. ������� ��������� ifdef/ifndef
        protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

        # ���� ��������� ������ ����
        for protectblock in protectblocks:
            filetext = get_file_text(file)  # ����� ����� ����� ����� ��������� ifdef/ifndef

            # ������ � ���� ������ protect �����
            write_text_to_file(file, protectblock)

            # �������� ��� �������������� � protect �����
            allind_search_and_replace(file)

            # ������ ������ ������ ������ �� �����
            newprotectblock = get_file_text(file)

            # ������ � ���� ������ � ������������ protect ������
            write_text_to_file(file, filetext.replace("`pragma protect on" + protectblock
                                                                      + "`pragma protect off", newprotectblock))

    else:
        return


# �-� ������ � ������ ����� ���������������, ����� input/output/inout � �������� ������
def module_search_and_replace_wo_inout(file, module):
    filetext = get_file_text(file)  # ����� �����

    moduleblock = get_module_blocks(filetext, module)

    # ���� ����� ������, �� ������������ ���
    if moduleblock:

        # ��������� ifdef/ifndef
        preobfuscator_ifdef(file)

        moduletext = get_module_blocks(filetext, module)  # ����� ����� ������

        # instance �������������� (�����)
        instances = search_instances(moduletext)

        # ������� ����� instance, ����� ��� �� ����������� ����� � ���������
        decrypt_table_instances = preobfuscator_instance(file)  # ������� ���������� ������ instance

        filetext = get_file_text(file)  # ����� ����� ����� �������� instance ��������
        newmoduletext = get_module_blocks(filetext, module)  # ����� ������ �����
        # �������� instance ��������

        inouts = search_inouts(newmoduletext)  # ������ ���� input/output/inout ���������������

        defines = re.findall(r"`define +(\w+)", newmoduletext)  # ������ ��������������� define

        # ������ ����� � ������������ ��� �������������� ������� ���������������
        # � ������ �������� ������ ���������������
        base = base_ind_search(newmoduletext, ["wire", "reg", "parameter", "localparam", "byte", "shortint",
                                               "int", "integer", "longint", "bit", "logic", "shortreal",
                                               "real", "realtime", "time", "event"])

        enums = enum_ind_search(newmoduletext)  # �������������� enums

        structs = re.findall(r"\Wstruct[\w|\W]+?} *(\w+);", newmoduletext)  # ������ ��������������� struct

        typedefs = re.findall(r"\Wtypedef[\w|\W]+?} *(\w+);", newmoduletext)  # ������ ��������������� typedef

        # �������� ��������� ��������������� typedef �� enums � struct
        for a in structs:
            if a in typedefs:
                structs.remove(a)
        for a in enums:
            if a in typedefs:
                enums.remove(a)

        # ����� ���������������, ���� typedef'��
        for typedef in typedefs:
            base_typedef = re.findall(typedef + r" +(.*?[,;\n)=])", newmoduletext)
            for i in range(len(base_typedef)):
                base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # ���������� ��������� ��������������� � base

        # ����� ��������������� ������� � �������
        funcs = re.findall(r"(?:task|function) +[\w|\W]+?(\w+)[ \n]*(?:\(|#\(|;)", filetext)

        # ��� �������������� (��� ��������)
        allind = set(defines + base + enums + structs + typedefs + funcs + instances)

        # �������� �� ������ allind ��������� input/output/inout ���������������
        delete_inouts(inouts, allind)

        # �������� ��������������� � �������� ������� ������������ � ������
        decrypt_table = {}
        encrypt_file(allind, file, newmoduletext, decrypt_table)

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

        # ��������� ���� �� � ������ ���������
        modules_wp = re.findall(r"\Wparameter\W",
                                newmoduletext)
        newfiletext = get_file_text(file)  # ����� ����� ����� �������� ��������� ���������������

        # ��������� instance ����� (����� ��������� instance ������ � ������ ������,
        # �.�. ��� ����� ���� � ����� ����� � ��������� �������,
        # � �������������� � ����� ����� ���� ���� �������� ����� � �������� instance ��������)
        for decr_inst in decrypt_table_instances:
            newfiletext = newfiletext.replace(decr_inst, decrypt_table_instances[decr_inst])
        # �������������� ���������� ������������� ����� � ��������������� instance ���������� � ����
        write_text_to_file(file, newfiletext)

        # ���� ������ �������� � �����������, �� �������� �� � ������ ������
        if modules_wp:
            # �������� ��� instance ����� � ������ ������ (������ ���������)
            # ������� ������ ��� ������
            change_instances_ports_allf([module], inv_decrypt_table)

        # ������ ������ ������ �� ����� ����� ��������� instance ������ �� ���� ������
        newfiletext = get_file_text(file)

        # �������� �������������� instance
        for inst in instances:
            newfiletext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", newfiletext)

        # ������� ���� � �������� ������������
        write_decrt_in_file(file, decrypt_table)

        # ������ � ���� ����� � ������������ ������ module
        write_text_to_file(file, newfiletext)

    else:
        print(module + " in " + file + " not found")
        return


# �-� ������ � ������ ���������� ���� ��������������� (input/output/inout, wire, reg, module, instance, parameter)
def ind_search_and_replace(file, ind):
    # ��������� ifdef/ifndef
    preobfuscator_ifdef(file)

    # ������� ����� instance, ����� ��� �� ����������� ����� � ���������
    decrypt_table_instances = preobfuscator_instance(file)  # ������� ���������� ������ instance

    filetext = get_file_text(file)  # ����� �����

    decrypt_table = {}  # ������� ������������ ��� ���������� ���������������

    allind = []  # ������ ���� ���������������

    # ���������
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # ���� ��������� ��� �������������� - "�������", �� �������� ��������������� �����
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        # ����� ���� ��������������� ���� ind
        allind = base_ind_search(filetext, [ind])

        # ������������ �� �����
        if ind != "(?:input|output|inout)":

            # ������������ parameter
            if ind == "parameter":

                # ���� ������ � �����������
                modules_with_par = []
                module_blocks = get_module_blocks(filetext)  # ������ �������, ��������� � ������ �����
                for module_block in module_blocks:
                    if re.search(r"\Wparameter\W", module_block):
                        modules_with_par.append(re.search(r"module +(\w+)", module_block)[1])

                # �������� ���������������
                encrypt_file(allind, file, filetext, decrypt_table)

                filetext = get_file_text(file)  # ����� ����� ����� �������� �������

                # ��������� instance ����� (����� ��������� instance ������ � ������ ������,
                # �.�. ��� ����� ���� � ����� ����� � ��������� �������,
                # � �������������� � ����� ����� ���� ���� �������� ����� � �������� instance ��������)
                for decr_inst in decrypt_table_instances:
                    filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])
                # �������������� ���������� ������������� ����� � ��������������� instance ���������� � ����
                write_text_to_file(file, filetext)

                # ���� ����� ������ � �����������, �� �������� �� � ������ ������
                if modules_with_par:
                    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

                    # �������� ��� instance ����� � ������ ������ (������ ���������)
                    change_instances_ports_allf(modules_with_par, inv_decrypt_table)

                # ������� ���� � �������� ������������
                write_decrt_in_file(file, decrypt_table)

            # ������������ reg, wire
            else:
                inouts = search_inouts(filetext)

                if ind == "wire":  # ��������� ��������� wire
                    allind += re.findall(r"wire +struct[\w :\[\]\-`]*?\{[\w|\W]*?} *(\w+)[,;\n)=]", filetext)

                # ������� input/output/inout ����� �� allind
                delete_inouts(inouts, allind)

                # �������� ��������������� � �������� ������� ������������
                encrypt_file(allind, file, filetext, decrypt_table)

                filetext = get_file_text(file)  # ����� ����� ����� ��������

                # ��������� instance �����
                for decr_inst in decrypt_table_instances:
                    filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

                write_text_to_file(file, filetext)
                write_decrt_in_file(file, decrypt_table)

        # ���� ������������ input/output/inout �����, �� ���� � ������ ������ ���������� ����� instance
        # �������� �������������� �������
        else:
            modules = get_modules(filetext)  # ������ �������, ��������� � ������ �����

            # �������� ���������������
            encrypt_file(allind, file, filetext, decrypt_table)

            filetext = get_file_text(file)  # ����� ����� ����� �������� �������

            inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

            # ��������� instance ����� (����� ��������� instance ������ � ������ ������,
            # �.�. ��� ����� ���� � ����� ����� � ��������� �������,
            # � �������������� � ����� ����� ���� ���� �������� ����� � �������� instance ��������)
            for decr_inst in decrypt_table_instances:
                filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])
            # �������������� ���������� ������������� ����� � ��������������� instance ���������� � ����
            write_text_to_file(file, filetext)

            # �������� ��� instance ����� � ������ ������, �� �� �������� �������� ������ ������� modules
            change_instances_ports_allf(modules, inv_decrypt_table)

            # ������� ���� � �������� ������������
            write_decrt_in_file(file, decrypt_table)

    # ���� ��������� ��� �������������� module - �� �������� �������������� ������� � ���
    # instance �������� � ������ ������
    elif ind == "module":

        # ����� ��������������� �������
        allind = get_modules(filetext)

        # �������� ���������������
        encrypt_file(allind, file, filetext, decrypt_table)

        filetext = get_file_text(file)  # ����� ����� ����� �������� �������

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

        # ��������� instance ����� (����� ��������� instance ������ � ������ ������,
        # �.�. ��� ����� ���� � ����� ����� � ��������� �������,
        # � �������������� � ����� ����� ���� ���� �������� ����� � �������� instance ��������)
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])
        # �������������� ���������� ������������� ����� � ��������������� instance ���������� � ����
        write_text_to_file(file, filetext)

        # �������� ��� ���� instance ������ � ������ ������
        change_instances_ports_allf(allind, inv_decrypt_table)

        # ������� ���� � �������� ������������
        write_decrt_in_file(file, decrypt_table)

    # ������ instance ���������������
    elif ind == "instance":

        # ��������� instance �����
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # ����� ���� instance ���������������
        allind = search_instances(filetext)

        # �������� instance ��������������� � �������� ������� ������������
        encrypt_text(allind, "", decrypt_table)
        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������
        for inst in allind:
            filetext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", filetext)

        # ������ ���������������� ������
        write_text_to_file(file, filetext)

        write_decrt_in_file(file, decrypt_table)

    # ������
    else:
        print("literal not correct")
        return


# �-� ������ � ������ ����� ���������������
def allind_search_and_replace(file):

    # ��������� ifdef/ifndef
    preobfuscator_ifdef(file)

    filetext = get_file_text(file)  # ����� �����

    # instance �������������� (�����)
    instances = search_instances(filetext)

    # ������� ����� instance, ����� ��� �� ����������� ����� � ���������
    decrypt_table_instances = preobfuscator_instance(file)  # ������� ���������� ������ instance

    filetext = get_file_text(file)  # ����� ����� ����� ifdef ��������� � �������� instance ��������

    modules = get_modules(filetext)  # ������ �������, ��������� � ������ �����

    defines = re.findall(r"`define +(\w+)", filetext)  # ������ ��������������� define

    # ������ ����� � ������������ ��� �������������� ������� ���������������
    # � ������ �������� ������ ���������������
    base = base_ind_search(filetext, ["input", "output", "inout", "wire", "reg",
                                      "parameter", "localparam", "byte", "shortint",
                                      "int", "integer", "longint", "bit", "logic", "shortreal",
                                      "real", "realtime", "time", "event"])

    enums = enum_ind_search(filetext)  # ������ ��������������� enums

    structs = re.findall(r"\Wstruct[\w|\W]+?} *(\w+);", filetext)  # ������ ��������������� struct

    typedefs = re.findall(r"\Wtypedef[\w|\W]+?} *(\w+);", filetext)  # ������ ��������������� typedef

    # �������� ��������� ��������������� typedef �� enums � struct
    for a in structs:
        if a in typedefs:
            structs.remove(a)
    for a in enums:
        if a in typedefs:
            enums.remove(a)

    # ����� ���������������, ���� typedef'��
    for typedef in typedefs:
        base_typedef = re.findall(typedef + r" +(.*?[,;\n)=])", filetext)
        for i in range(len(base_typedef)):
            base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # ���������� ��������� ��������������� � base

    # ����� ��������������� ������� � �������
    funcs = re.findall(r"(?:task|function) +[\w|\W]+?(\w+)[ \n]*(?:\(|#\(|;)", filetext)

    # ��� �������������� (��� ��������)
    allind = set(defines + base + enums + structs + typedefs + modules + funcs + instances)  # ��� ��������������

    # �������� ��������������� � �������� ������� ������������
    decrypt_table = {}
    encrypt_file(allind, file, filetext, decrypt_table)

    filetext = get_file_text(file)  # ����� ����� ����� �������� ����� ���������������

    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # ������������ ������� ������������

    # ��������� instance ����� (����� ��������� instance ������ � ������ ������,
    # �.�. ��� ����� ���� � ����� ����� � ��������� �������,
    # � �������������� � ����� ����� ���� ���� �������� ����� � �������� instance ��������)
    for decr_inst in decrypt_table_instances:
        filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])
    # �������������� ���������� ������������� ����� � ��������������� instance ���������� � ����
    write_text_to_file(file, filetext)

    # �������� ��� instance ����� � ������ ������, �� �� �������� �������� ������ ������� modules
    change_instances_ports_allf(modules, inv_decrypt_table)

    filetext = get_file_text(file)  # ����� ����� ����� ��������� instance ������ �� ���� ������

    # ������� ���� � �������� ������������
    write_decrt_in_file(file, decrypt_table)

    # ������� ������� ������ ������ instance �����
    for invdt in inv_decrypt_table:
        ports = set(re.findall(r"\( *" + invdt + r"\W", filetext))
        for port in ports:
            # �������� ��������� ������� ��� ���������� ������ ����������� ���������
            port = regexp_to_str(port)

            filetext = re.sub(port, "(" + inv_decrypt_table[re.search(r"\w+", port)[0]] + port[-1], filetext)

    # �������� �������������� instance
    for inst in instances:
        filetext = re.sub(inst + r"[ \n]*\(", inv_decrypt_table[inst] + "(", filetext)

    # ������ ���������������� ������
    write_text_to_file(file, filetext)


# �-� ������ �������� ������ instance ��������, �� � ����� �� ���� ������ �������
def change_instances_ports_allf(modules, decr_table):
    files = get_sv_files(os.curdir)  # ��� �����

    # ���� ��������� ������ �� ���� ������
    for file in files:

        # ������������ ifdef/ifndef
        preobfuscator_ifdef(file)

        decrypt_table_instances = {}  # ������� ������������ ������ instance �������

        filetext = get_file_text(file)  # ����� �����

        # ���� ��������� instance �������� ������� modules
        for module in modules:

            # ������� ��� instance ������� (�� �����)
            # instances = search_instance_blocks(filetext)
            instances = re.findall(r"(?<!module)[ \n]+(" + module + r"[ \n]+\w+[ \n]*\([\w|\W]*?\) *;)", filetext)
            instances += re.findall(
                r"(?<!module)[ \n]+(" + module + r"[ \n]+#\([\w|\W]*?\)[ \n]*\w+[ \n]*\([\w|\W]*?\) *;)", filetext)

            # ���� ����� ������� ����������, �� ������������ ��
            if instances:

                # ���� ��������� ������ ������� instance
                for instance in instances:

                    # ��������� ������ ����� �������
                    oldinstance = instance

                    # ����� ���� ������ �������
                    inouts = re.findall(r"\.(\w+)", instance)

                    # ���� ������ �������� ������ �� ��������������� � ������� decr_table
                    for inout in inouts:
                        if inout in decr_table:
                            port = re.search(r"\."+inout+r"\W", instance)[0]
                            instance = instance.replace(port, "." + decr_table[inout] + port[-1])

                            # ��������� � ������� decrypt_table_instances ��������������� ������ �� decr_table
                            decrypt_table_instances[decr_table[inout]] = inout

                    # ���� ���������� - �������� �������� ������ instance ������� � ��������� � �������
                    # decrypt_table_instances
                    if module in decr_table:
                        instance = re.sub(module, decr_table[module], instance, 1)  # �������� ������ 1 ���������
                        decrypt_table_instances[decr_table[module]] = module

                    # �������� ����� �� ����������
                    filetext = filetext.replace(oldinstance, instance)

            # ���� ����� �������� ���, �� ���������� �����
            else:
                continue
        # ���� ������� decrypt_table_instances �� �����, �� ���������� �� � ���� ������ ������������
        if decrypt_table_instances:
            write_decrt_in_file(file, decrypt_table_instances)

        # ������ ����������� ������ � ����
        write_text_to_file(file, filetext)