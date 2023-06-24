import json
import os
import re
import scanfiles

#ф-€ запускающа€ препроцессинг sv файлов
def launch():
    json_file = open(r"ifdefprocessing.json", "r")
    json_struct = json.load(json_file)

    files = []  # список файлов дл€ которых проводитс€ работа
    if json_struct["conf"]["allfiles"]:
        files = scanfiles.getsv(os.curdir)  # добавл€ем файлы всего проекта
    else:
        files.append(json_struct["conf"]["filename"])  # добавл€ем 1 необходимый файл

    # добавление include файлов
    if json_struct["tasks"]["a"]:

        # цикл по всем файлам
        for file in files:
            fileopen = open(file, "r")  # открытие файла
            filestr = fileopen.read()

            # измен€ем текст sv файла - замен€ем `include на текст соответствующего файла
            filestr = addincludes(json_struct, filestr)

            fileopen.close()  # закрытие файла
            fileopen = open(file, "w")
            fileopen.write(filestr)  # запись нового текста в файл


# ф-€ добавл€юща€ в текст sv файла include файлы (в том числе включа€ include включаемого файла)
def addincludes(json, filestr, included = []):

    # поиск всех include в файле (список без повторов)
    includes = list(set(re.findall(r"`include *\"[\w\.]+\"", filestr)))

    # оставл€ем только названи€ включаемых файлов
    for i in range(len(includes)):
        includes[i] = re.sub("`include +", '', includes[i])
        includes[i] = re.sub("\"", '', includes[i])

    # цикл по всем включаемым файлам
    for include in includes:
        existfile = False  # флаг существовани€ включаемого файла

        # цикл по всем директори€м, где должны хранитс€ include файлы
        for includepath in json["includes"]:

            # если файл в текущей директоии есть, то добавл€ем текст включаемого файла
            if os.path.exists(includepath+"\\"+include) and include not in included:
                existfile = True
                includetextopen = open(includepath+"\\"+include, "r")
                includetext = includetextopen.read()
                filestr = re.sub("`include *\""+include+"\"", includetext, filestr, 1)

                # удаление повтор€ющихс€ включений
                filestr = re.sub("`include *\"" + include + "\"", '', filestr)
                includetextopen.close()

                included.append(include)
                print(include)
                # includetextopen = open(includepath + "\\" + include, "w")
                # includetextopen.write(filestr)
                # includetextopen.close()
                break

        # если включаемый файл не был найден, то оставл€ем соответствующую пометку и идем к следующему файлу
        if not existfile:

            # добавл€ем пометку
            filestr = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" //file don't exist", filestr)

            # убираем включаемый файл из списка
            includes.remove(include)
            continue

    # если хот€бы 1 файл был добавлен, включаем и его файлы
    if len(includes) != 0:
        filestr = addincludes(json, filestr, included)

    return filestr

