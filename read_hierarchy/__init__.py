# СКРИПТ ЧТЕНИЯ ИЕРАРХИИ ПРОЕКТА
# настройка конфигурации осуществляется в "read_hierarchy.json"
import obfuscator
from read_hierarchy.base_funcs import *

# ------------------------------ИНИЦИАЛИЗАЦИЯ_ГЛОБАЛЬНЫХ_ПЕРЕМЕННЫХ------------------------------ #

json_struct = get_json_struct(r"jsons/read_hierarchy.json")

files = get_sv_files(os.curdir)  # sv файлы всего проекта

# ifdef/ifndef обработка всех фалйов
for file_g in files:
    obfuscator.preobfuscator_ifdef(file_g)

modules = get_all_modules()  # все модули


# ------------------------------ЗАПУСК_ЧТЕНИЯ_ИЕРАРХИИ------------------------------ #

# запуск чтения иерархии
def launch():
    # восстановление структуры вызовов модулей
    if json_struct["tasks"]["CallStructure"]:
        restoring_call_structure()

    # поиск иерархических путей ко всем обьектам модулей
    if json_struct["tasks"]["AllObjects"]:
        search_allmodule_objects()

    # разделение файлов с несколькими модулями
    if json_struct["tasks"]["SplittingModules"]:
        splitting_modules_by_files()