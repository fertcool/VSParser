import json
import os
import re
from queue import Queue
import obfuscator
import scanfiles

json_file = open(r"read_hierarchy.json", "r")
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

    # if json_struct["tasks"]["b"]:
    #
    #
    #
    #
    # if json_struct["tasks"]["c"]:


def restoring_call_structure(dir):

    inst_dict = get_inst_dict(dir)
    inst_in_modules_dict = get_insts_in_modules(dir)

    project_struct_report(json_struct["report_filename"], inst_dict, inst_in_modules_dict)
    project_objects_inst_report(json_struct["report_filename"], inst_dict, inst_in_modules_dict)


def get_inst_dict(dir):

    instances = {}  # словарь instance обьектов

    for file in files:
        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст файла
        fileopen.close()


        # цикл поиска instance модуля module из списка modules в файле
        for module in modules:

            # поиск
            searched_instance = re.findall(module + r" +(\w+) *\([\w|\W]+?\) *;", filetext)
            searched_instance += re.findall(module + r" *# *\([\w|\W]+?\) *(\w+) *\([\w|\W]+?\);", filetext)

            # добавление в список
            if searched_instance:
                for inst in searched_instance:
                    instances[inst] = module
            else:
                continue


    return instances

def get_insts_in_modules(dir):
    insts_in_modules_dict = {}
    insts = get_inst_dict(dir)

    for file in files:
        fileopen = open(file, "r")  # открытие файла
        filetext = fileopen.read()  # текст файла
        fileopen.close()

        moduleblocks = re.findall(r"module +[\w|\W]+?endmodule *: *\w+[.\n]", filetext)


        for moduleblock in moduleblocks:

            modulename = re.search("endmodule *: *(\w+)[.\n]", moduleblock)[1]
            insts_in_modules_dict[modulename] = []

            for inst in insts:
                insts_in_modules_dict[modulename] += re.findall(r"\w+ +(" + inst + r") *\(", moduleblock)
                insts_in_modules_dict[modulename] += re.findall(r"\) *(" + inst + r") *\(", moduleblock)

    return insts_in_modules_dict

def get_root_module(inst_dict, inst_in_modules_dict):
    root = ""
    for module in inst_in_modules_dict:
        if inst_in_modules_dict[module]:
            no_link_flag = True
            for inst in inst_dict:
                if inst_dict[inst] == module:
                    no_link_flag = False
            if no_link_flag:
                root = module

    return root


def project_struct_report(filename, inst_dict, inst_in_modules_dict):
    fileopen = open(filename, "a")
    fileopen.write("\n\n*------------------------------PROJECT_CALL_STRUCTURE------------------------------*\n")
    root = get_root_module(inst_dict, inst_in_modules_dict)

    used = {}
    for inst in inst_dict:
        used[inst] = False
    modules_queue = Queue()

    fileopen.write("ROOT: " + root + " -> " + str(inst_in_modules_dict[root])+"\n\n")
    for inst in inst_in_modules_dict[root]:
        modules_queue.put(inst)

    while not modules_queue.empty():
        cur_module = modules_queue.get()

        fileopen.write(cur_module + " ( "+inst_dict[cur_module]+" ) -> " + str(
            inst_in_modules_dict[inst_dict[cur_module]])+"\n\n")

        for inst in inst_in_modules_dict[inst_dict[cur_module]]:
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

    fileopen.close()


def project_objects_inst_report(filename, inst_dict, inst_in_modules_dict):
    fileopen = open(filename, "a")
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")
    root = get_root_module(inst_dict, inst_in_modules_dict)

    used = {}
    for inst in inst_dict:
        used[inst] = False
    modules_queue = Queue()

    fileopen.write("ROOT: " + root + "\n\n")
    for inst in inst_in_modules_dict[root]:
        modules_queue.put(root+'.' + inst)

    while not modules_queue.empty():
        cur_module = modules_queue.get()

        fileopen.write(cur_module + "\n\n")

        for inst in inst_in_modules_dict[inst_dict[re.search(r"\.(\w+)$", cur_module)[1]]]:
            if not used[inst]:
                modules_queue.put(cur_module+'.'+inst)
                used[inst] = True

    fileopen.close()

def project_allobjects_report(filename, inst_dict, inst_in_modules_dict):
    fileopen = open(filename, "a")
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")
    root = get_root_module(inst_dict, inst_in_modules_dict)

    modules_with_objects = scanfiles.getallmodules(os.curdir, False)

    used = {}
    for inst in inst_dict:
        used[inst] = False
    modules_queue = Queue()

    fileopen.write("ROOT: " + root + "\n\n")

    for typeobject in modules_with_objects[root]:
        for i in range(len(modules_with_objects[root][typeobject])):
            fileopen.write(root+"."+modules_with_objects[root][typeobject][i]+" ( "+typeobject+" ) \n")

    for inst in inst_in_modules_dict[root]:
        modules_queue.put(root+'.' + inst)

    while not modules_queue.empty():
        cur_module = modules_queue.get()

        for typeobject in modules_with_objects[inst_dict[re.search(r"\.(\w+)$", cur_module)[1]]]:
            for i in range(len(modules_with_objects[inst_dict[re.search(r"\.(\w+)$", cur_module)[1]]][typeobject])):
                fileopen.write(cur_module + "." + modules_with_objects[inst_dict[re.search(r"\.(\w+)$", cur_module)[1]]][typeobject][i] + " ( " + typeobject + " ) \n")

        for inst in inst_in_modules_dict[inst_dict[re.search(r"\.(\w+)$", cur_module)[1]]]:
            if not used[inst]:
                modules_queue.put(cur_module + '.' + inst)
                used[inst] = True

    fileopen.close()
def search_allmodule_objects(dir):
    
    inst_dict = get_inst_dict(dir)
    inst_in_modules_dict = get_insts_in_modules(dir)

    project_allobjects_report(json_struct["report_filename"], inst_dict, inst_in_modules_dict)
    
    


