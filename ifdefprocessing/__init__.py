# СКРИПТ РАБОТЫ С IFDEF/IFNDEF ВЕТКАМИ И ВКЛЮЧЕНИЯ INCLUDE ФАЙЛОВ
# настройка конфигурации осуществляется в "ifdefprocessing.json"
# перед ifdef обработкой удаляются комментарии с define


from ifdefprocessing.idef import ifdef_pr_forfile
from ifdefprocessing.include import include_for_file
from work_with_files import *

json_struct = get_json_struct(r"jsons/ifdefprocessing.json")
# ------------------------------ЗАПУСК_СКРИПТА------------------------------ #

# ф-я запускающая препроцессинг sv файлов
def launch():

    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = get_sv_files(os.curdir)  # добавляем файлы всего проекта
    else:
        files.append(json_struct["conf"]["filename"])  # добавляем 1 необходимый файл

    # добавление include файлов
    if json_struct["tasks"]["IncludePr"]:

        # цикл по всем файлам
        for file in files:
            include_for_file(file)

    # обработка ifdef/ifndef
    if json_struct["tasks"]["IfdefPr"]:

        # цикл по всем файлам
        for file in files:
            ifdef_pr_forfile(file)