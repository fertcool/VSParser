import json
import os
import re
import scanfiles

#ф-я запускающая препроцессинг sv файлов
def launch():
    json_file = open(r"ifdefprocessing.json", "r")
    json_struct = json.load(json_file)

    files = []  # список файлов для которых проводится работа
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.getsv(os.curdir)  # добавляем файлы всего проекта
    else:
        files.append(json_struct["conf"]["filename"])  # добавляем 1 необходимый файл

    # добавление include файлов
    if json_struct["tasks"]["a"]:

        # цикл по всем файлам
        for file in files:
            fileopen = open(file, "r")  # открытие файла
            filestr = fileopen.read()

            # изменяем текст sv файла - заменяем `include на текст соответствующего файла
            filestr = addincludes(json_struct, filestr)

            fileopen.close()  # закрытие файла
            fileopen = open(file, "w")
            fileopen.write(filestr)  # запись нового текста в файл


# ф-я добавляющая в текст sv файла include файлы (в том числе включая include включаемого файла)
def addincludes(json, filestr, included = None):

    if included is None:
        included = []

    # поиск всех include в файле (расположенных последовательно)
    includes = re.findall(r"`include *\"[\w\.]+\"", filestr)

    # оставляем только названия включаемых файлов
    for i in range(len(includes)):
        includes[i] = re.sub("`include +", '', includes[i])
        includes[i] = re.sub("\"", '', includes[i])

    # цикл по всем включаемым файлам
    for include in includes:
        existfile = False  # флаг существования включаемого файла

        # цикл по всем директориям, где должны хранится include файлы
        for includepath in json["includes"]:

            # если файл в текущей директоии есть (и он еще не был включен)
            # , то добавляем текст включаемого файла
            if os.path.exists(includepath+"\\"+include) and include not in included:
                existfile = True
                includetextopen = open(includepath+"\\"+include, "r")
                includetext = includetextopen.read()

                # вставляем в файл на место 1 включения
                filestr = re.sub("`include *\""+include+"\"", includetext, filestr, 1)

                # удаление повторяющихся включений
                filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                 filestr)
                includetextopen.close()

                # добавляем вставленный файл в список включенных
                included.append(include)

                # заново просматриваем файл (ищем снова включения)
                filestr = addincludes(json, filestr, included)

                # выходим, т.к. уже нащли и вставили файл
                break

        # если включаемый файл не был найден, то оставляем соответствующую пометку и идем к следующему файлу
        if not existfile:

            # добавляем пометку
            if include not in included: # если файл не был включен
                filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file don't exist", filestr)
            else: # если файл был включен
                filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                 filestr)
            continue

    return filestr

