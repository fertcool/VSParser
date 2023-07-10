import json
import os
import re
from queue import Queue
import obfuscator
import scanfiles

json_file = open(r"jsons/read_hierarchy.json", "r")
json_struct = json.load(json_file)

files = scanfiles.getsv(os.curdir)  # добавляем файлы всего проекта
for file in files:
    obfuscator.preobfuscator_ifdef(file)

# все модули
modules = scanfiles.getallmodules(os.curdir)
def launch():


    # обфускация по всем индентификаторам
    if json_struct["tasks"]["a"]:
        restoring_call_structure(os.curdir)
    
    if json_struct["tasks"]["b"]:
        search_allmodule_objects(os.curdir)

    if json_struct["tasks"]["c"]:
        splitting_modules_by_files(os.curdir)


def restoring_call_structure(dir):


    inst_in_modules_dict = get_insts_in_modules(dir)

    # count_i = 0
    # for i in inst_in_modules_dict:
    #     print(i+" - "+count_i, end="")
    #     count_i1 = 0
    #     for i1  in inst_in_modules_dict[i]:
    #         for i2 in inst_in_modules_dict:
    #             if i2==i1

    project_struct_report(json_struct["report_filename"], inst_in_modules_dict)
    project_objects_inst_report(json_struct["report_filename"], inst_in_modules_dict)

def get_inst_list(insts_in_modules_dict):
    insts = []

    for module in insts_in_modules_dict:
        insts+=insts_in_modules_dict[module]

    return insts
def get_insts_in_modules(dir):

    insts_in_modules_dict = {}  #jhjkhjk

    for file in files:
        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст файла
        fileopen.close()

        moduleblocks = re.findall(r"module +[\w|\W]+?endmodule *: *\w+", filetext)
        for moduleblock in moduleblocks:
            modulename = re.search("endmodule *: *(\w+)", moduleblock)[1]

            insts_in_modules_dict[modulename] = []

            # цикл поиска instance модуля module из списка modules в файле
            for module in modules:

                # поиск
                searched_instance = re.findall(module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)
                searched_instance += re.findall(module + r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)

                # добавление в список
                if searched_instance:
                    for inst in searched_instance:
                        insts_in_modules_dict[modulename].append(inst+"("+module+")")
                else:
                    continue


    return insts_in_modules_dict

# def get_insts_in_modules(dir):
#     insts_in_modules_dict = {}
#     insts = get_inst_dict(dir)
#
#     for file in files:
#         fileopen = open(file, "r")  # открытие файла
#         filetext = fileopen.read()  # текст файла
#         fileopen.close()
#
#         moduleblocks = re.findall(r"module +[\w|\W]+?endmodule *: *\w+", filetext)
#
#         for moduleblock in moduleblocks:
#
#             modulename = re.search("endmodule *: *(\w+)", moduleblock)[1]
#             insts_in_modules_dict[modulename] = []
#
#             for inst in insts:
#                 insts_in_modules_dict[modulename] += re.findall(r"\w+ +(" + inst + r") *\(", moduleblock)
#                 insts_in_modules_dict[modulename] += re.findall(r"\) *(" + inst + r") *\(", moduleblock)
#
#     return insts_in_modules_dict

def get_roots_modules(inst_in_modules_dict):
    roots = []
    insts = get_inst_list(inst_in_modules_dict)

    for module in inst_in_modules_dict:
        if inst_in_modules_dict[module]:
            no_link_flag = True
            for inst in insts:
                if re.search(r"\((\w+)\)", inst)[1] == module:
                    no_link_flag = False
            if no_link_flag:
                roots.append(module)


    return roots


def project_struct_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")
    fileopen.write("\n\n*------------------------------PROJECT_CALL_STRUCTURE------------------------------*\n")

    roots = get_roots_modules(inst_in_modules_dict)

    insts = get_inst_list(inst_in_modules_dict)

    used = {}
    for inst in insts:
        used[inst] = False
    modules_queue = Queue()

    fileopen.write("ROOTS: "+str(roots)+"\n\n")
    for root in roots:
        fileopen.write("ROOT: " + root + " -> " + str(inst_in_modules_dict[root])+"\n\n")
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(inst)

    while not modules_queue.empty():
        cur_module = modules_queue.get()

        fileopen.write(cur_module + " -> " + str(
            inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]])+"\n\n")

        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

    fileopen.close()


def project_objects_inst_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")

    roots = get_roots_modules(inst_in_modules_dict)

    modules_queue = Queue()

    fileopen.write("ROOTS: " + str(roots) + "\n\n")
    for root in roots:
        fileopen.write("ROOT: " + root + "\n\n")
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root+'.' + inst)

    while not modules_queue.empty():
        cur_module = modules_queue.get()

        fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "\n\n")

        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1]+'.'+inst)


    fileopen.close()

def project_allobjects_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")
    roots = get_roots_modules(inst_in_modules_dict)

    modules_with_objects = scanfiles.getallmodules(os.curdir, False)

    modules_queue = Queue()

    fileopen.write("ROOTS: " + str(roots) + "\n\n")
    for root in roots:
        for typeobject in modules_with_objects[root]:
            for i in range(len(modules_with_objects[root][typeobject])):
                fileopen.write(root+"."+modules_with_objects[root][typeobject][i]+" ( "+typeobject+" ) \n")

        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root+'.' + inst)

    while not modules_queue.empty():
        cur_module = modules_queue.get()

        for typeobject in modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]]:
            for i in range(len(modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject])):
                fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "." + modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject][i] + " ( " + typeobject + " ) \n")

        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
                modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)


    fileopen.close()
def search_allmodule_objects(dir):
    

    inst_in_modules_dict = get_insts_in_modules(dir)

    project_allobjects_report(json_struct["report_filename"], inst_in_modules_dict)
    
def splitting_modules_by_files(dir):

    for file in files:
        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст файла
        fileopen.close()

        moduleblocks = re.findall(r"module +[\w|\W]+?endmodule *: *\w+", filetext)

        if len(moduleblocks) > 1:

            for moduleblock in moduleblocks:
                modulename = re.search(r"endmodule *: *(\w+)", moduleblock)[1]

                filetext_with_cur_module = filetext
                for moduleblock_another in moduleblocks:
                    if moduleblock_another == moduleblock:
                        continue
                    else:
                        filetext_with_cur_module = filetext_with_cur_module.replace(moduleblock_another, '')

                newfileopen = open(re.sub(r"[\w\.]+$", modulename, file) + ".sv", "w")
                print(modulename)
                newfileopen.write(filetext_with_cur_module)
                newfileopen.close()

            os.remove(file)








