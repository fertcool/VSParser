from queue import Queue
from read_hierarchy.utilities import *

# ------------------------------ФУНКЦИИ_ПОИСКА_И_ПЕЧАТИ_ИЕРАРХИИ------------------------------ #

# ф-я поиска корневых модулей
def get_roots_modules(inst_in_modules_dict):
    roots = []  # корневые модули

    insts = get_inst_list(inst_in_modules_dict)  # список всех instance обьектов

    # цикл проверик каждого модуля на то является ли он корневым
    for module in inst_in_modules_dict:

        # если список instance обьектов модуля не пуст - то проверяем его
        if inst_in_modules_dict[module]:

            # флаг - нет ли на instance обьект ссылки, т.е. этот модуль не имеет нигде экземпляров,
            # т.е. это флаг корневого модуля
            no_link_flag = True

            # проходимся по всем instance обьектам, чтобы найти хотя бы 1 ссылку на модуль
            for inst in insts:

                # ссылка на обьект есть, если текущий обьект имеет тип модуля module
                if re.search(r"\((\w+)\)", inst)[1] == module:
                    no_link_flag = False

            # если флаг был изменен, то добавляем корневой модуль
            if no_link_flag:
                roots.append(module)

    return roots


# ф-я чтения струкутры вызовов модулей проекта и записи соответствующего отчета в файл
def project_struct_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # открытие файла

    fileopen.write("\n\n*------------------------------PROJECT_CALL_STRUCTURE------------------------------*\n")

    # получаем список корневых модулей
    roots = get_roots_modules(inst_in_modules_dict)

    # получаем список всех instance обьектов
    insts = get_inst_list(inst_in_modules_dict)

    used = {}  # словарь добавленных в отчет instance обьектов (чтобы не было повторных записей)
    for inst in insts:
        used[inst] = False

    modules_queue = Queue()  # очередь instance обьектов

    # печать корневых модулей
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # печать instance обьектов корневых модулей
    for root in roots:
        fileopen.write("ROOT: " + root + " -> " + str(inst_in_modules_dict[root]) + "\n\n")

        # добавление instance обьектов в корневых модулях в очередь
        for inst in inst_in_modules_dict[root]:
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

    # цикл печати instance обьектов в отчет (что-то типо поиска в ширину)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # текущий модуль, взятый из очереди

        # печать списка instance обьектов текущего модуля
        fileopen.write(cur_module + " -> " + str(
            inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]) + "\n\n")

        # цикл добавления instance обьектов текущего модуля в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            if not used[inst]:
                modules_queue.put(inst)
                used[inst] = True

    fileopen.close()  # закрытие файла


# ф-я поиска и печати в отчет иерархических путей ко всем instance обьектам
def project_objects_inst_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # открытие файла
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")

    # получаем список корневых модулей
    roots = get_roots_modules(inst_in_modules_dict)

    modules_queue = Queue()  # очередь instance обьектов

    # печать корневых модулей
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # печать instance обьектов корневых модулей
    for root in roots:
        fileopen.write("ROOT: " + root + "\n\n")

        # добавление instance обьектов в корневых модулях в очередь
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root + '.' + inst)

    # цикл печати instance обьектов в отчет (что-то типо поиска в ширину)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # текущий instance обьект, взятый из очереди

        # печатаем текущий instance обьект (без типа в круглых скобках)
        fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "\n\n")

        # цикл добавления instance обьектов текущего модуля в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)

    fileopen.close()  # закрытие файла


# ф-я поиска и печати иерархических путей всех обьектов (reg, net, instance, port)
def project_allobjects_report(filename, inst_in_modules_dict):
    fileopen = open(filename, "a")  # открытие файла
    fileopen.write("\n\n*------------------------------PROJECT_OBJECTS------------------------------*\n")

    # получаем список корневых модулей
    roots = get_roots_modules(inst_in_modules_dict)

    # получаем словарь модулей со всеми их обьектами (reg, net, instance, port)
    modules_with_objects = get_all_modules(False)

    modules_queue = Queue()  # очередь instance обьектов

    # печать корневых модулей
    fileopen.write("ROOTS: " + str(roots) + "\n\n")

    # цикл печати обьектов (reg, net, instance, port) корневых модулей в отчет
    # и добавления instance обьектов корневых модулей в очередь
    for root in roots:

        # цикл по всем типам (reg, net, instance, port)
        for typeobject in modules_with_objects[root]:
            # цикл по всем обьектам конкретного типа
            for i in range(len(modules_with_objects[root][typeobject])):
                fileopen.write(root + "." + modules_with_objects[root][typeobject][i] + " ( " + typeobject + " ) \n")

        # добавление instance обьектов корневых модулей в очередь
        for inst in inst_in_modules_dict[root]:
            modules_queue.put(root + '.' + inst)

    # цикл печати иерархических путей всех обьектов (reg, net, instance, port)
    while not modules_queue.empty():

        cur_module = modules_queue.get()  # текущий instance обьект, взятый из очереди

        # цикл печати иерархических путей всех обьектов (reg, net, instance, port) текущего instance обьекта
        for typeobject in modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]]:
            for i in range(len(modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject])):
                fileopen.write(re.search(r"([\w\.]+)\(", cur_module)[1] + "." +
                               modules_with_objects[re.search(r"\((\w+)\)", cur_module)[1]][typeobject][
                                   i] + " ( " + typeobject + " ) \n")

        # цикл добавления instance обьектов текущего модуля в очередь
        for inst in inst_in_modules_dict[re.search(r"\((\w+)\)", cur_module)[1]]:
            modules_queue.put(re.search(r"([\w\.]+)\(", cur_module)[1] + '.' + inst)

    fileopen.close()  # закрытие файла