# СКРИПТ ОБФУСКАЦИИ ФАЙЛОВ
# настройка конфигурации осуществляется в "obfuscator.json"

# обфускация производится над идентификаторами:
# input / output / inout
# wire / reg
# module / function / task
# instance
# parameter / localparam
# byte / shortint / int / integer / longint / integer / bit / logic / shortreal / real
# realtime / time
# event
# enum / typedef
# `define
# перед обфускацией происходит include-ifdef обработка и удаление комментариев
# обфускация не производится над вызовами instance обьектов через "."
# если обфусцируются модули или их порты, параметры, то они заменяются и у instance экземпляров проекта


from obfuscator.base_funcs import *

json_struct = get_json_struct(r"jsons/obfuscator.json")

# ------------------------------ЗАПУСК_ОБФУСКАЦИИ------------------------------ #


def launch():
    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = get_sv_files(os.curdir)  # добавляем файлы всего проекта
    else:
        files.append(json_struct["conf"]["filename"])  # добавляем 1 необходимый файл

    # обфускация по всем идентификаторам
    if json_struct["tasks"]["AllObf"]:

        # цикл по всем файлам
        for file in files:
            allind_search_and_replace(file)

    # обфускация по выбранному классу идентификаторов (input/output/inout, wire, reg, module, instance, parameter)
    if json_struct["tasks"]["IndObf"]:

        # цикл по всем файлам
        for file in files:
            ind_search_and_replace(file, json_struct["literalclass"])

    # обфускация по идентификаторам input/output/inout в заданном модуле
    if json_struct["tasks"]["ModuleWoInoutsObf"]:

        # цикл по всем файлам
        for file in files:
            module_search_and_replace_wo_inout(file, json_struct["module"])

    # обфускация в рамках (protect on - protect off)
    if json_struct["tasks"]["ProtectObf"]:

        # цикл по всем файлам
        for file in files:
            ind_search_and_replace_protect(file)