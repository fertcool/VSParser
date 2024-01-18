# СКРИПТ ДЕШИВРОВКИ ФАЙЛОВ ПОСЛЕ ОБФУСКАЦИИ
# настройка конфигурации осуществляется в "deobfuscator.json"

from obfuscator.deobfuscator.base_funcs import *

allfiles = get_sv_files(os.curdir)  # добавляем файлы всего проекта

# ------------------------------ЗАПУСК_ДЕОБФУСКАЦИИ------------------------------ #


# запуск деобфускации
def launch():
    json_struct = get_json_struct(r"jsons/deobfuscator.json")

    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = get_sv_files(os.curdir)  # добавляем файлы всего проекта
    else:
        files.append(json_struct["conf"]["filename"])  # добавляем 1 необходимый файл

    # восстановление всего обфусцированного кода по таблицам соответствия
    if json_struct["tasks"]["AllDeobf"]:

        # цикл по всем файлам
        for file in files:
            decryptall(file)

    #  Частично восстановить исходный код из обфусцированного только для выбранного класса
    #  идентификаторов (input/output/inout, wire, reg, module, instance, parameter).
    if json_struct["tasks"]["IndDeobf"]:

        # цикл по всем файлам
        for file in files:
            decrypt_one_ind(file, json_struct["literalclass"])

    # Частично восстановить исходный код из обфусцированного только для портов ввода вывода заданного модуля
    if json_struct["tasks"]["ModuleInoutsDeobf"]:

        # цикл по всем файлам
        for file in files:
            decrypt_module_inout(file, json_struct["module"])
