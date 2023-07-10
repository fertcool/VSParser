import json
import os
import re
import scanfiles
import erase_comments

# ф-я запускающая препроцессинг sv файлов
def launch():
    json_file = open(r"jsons/ifdefprocessing.json", "r")
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
            include_for_file(file, json_struct)

    # обработка ifdef/ifndef
    if json_struct["tasks"]["b"]:
        # цикл по всем файлам
        for file in files:
            ifdef_pr_forfile(file, json_struct)


# ф-я добавляющая в текст sv файла include файлы (в том числе включая include включаемого файла)
def addincludes(json, filetext, included = None):

    if included is None:
        included = []

    # поиск всех include в файле (расположенных последовательно)
    includes = re.findall(r"`include *\"[\w\.]+\"", filetext)

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
                filetext = re.sub("`include *\""+include+"\"", includetext, filetext, 1)

                # удаление повторяющихся включений
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                 filetext)
                includetextopen.close()

                # добавляем вставленный файл в список включенных
                included.append(include)

                # заново просматриваем файл (ищем снова включения)
                filetext = addincludes(json, filetext, included)

                # выходим, т.к. уже нашли и вставили файл
                break

        # если включаемый файл не был найден, то оставляем соответствующую пометку и идем к следующему файлу
        if not existfile:

            # добавляем пометку
            if include not in included: # если файл не был включен
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file don't exist", filetext)
            else:  # если файл был включен
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                 filetext)
            continue

    return filetext


# ф-я добавления всех include файлов для 1 файла
def include_for_file(file, json):
    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()

    # изменяем текст sv файла - заменяем `include на текст соответствующего файла
    filetext = addincludes(json, filetext)

    fileopen.close()  # закрытие файла
    fileopen = open(file, "w")
    fileopen.write(filetext)  # запись нового текста в файл
    fileopen.close()


def ifdef_pr_forfile(file, json):
    #  удаляем комментарии с определениями
    erase_comments.delete(file, [r"/\* *`define *[\s|\S]*?\*/", r"// *`define *[^\n]*\n"], False)

    fileopen = open(file, "r")  # открытие файла
    filetext = fileopen.read()

    # цикл пока есть блоки ifdef или ifndef в файле
    while (re.search(r"`(?:ifndef|ifdef)[\s|\S]*?`endif", filetext)):

        # поиск всех блоков ifdef/ifndef (возможно с вложениями)
        ifdefs = re.findall(r"`(?:ifndef|ifdef)[\s|\S]*?`endif", filetext)

        # убираем вложения, если они есть (например ifdef...ifdef...endif -> ifdef...endif)
        for i in range(len(ifdefs)):
            ifs = re.findall(r"`(?:ifndef|ifdef) +\w+", ifdefs[i])
            if len(ifs) > 1:
                ifdefs[i] = re.search(r"[\s|\S]" + ifs[len(ifs) - 1] + r"[\s|\S]*?`endif", ifdefs[i])[0]
                ifdefs[i] = ifdefs[i][1:]

        # цикл обработки каждого блока
        for ifdef in ifdefs:

            index = filetext.find(ifdef)
            textbefore = filetext[:index]  # текст до блока

            defines = re.findall(r"`define +\w+", textbefore)  # все define до блока
            defines.extend(json["defines"])  # добавляем внешние define
            # оставляем только названия define
            for i in range(len(defines)):
                defines[i] = re.sub("`define +", '', defines[i])
                defines[i] = re.sub("\n", '', defines[i])

            # обработка блока
            newifdef = ifblockprocessing(ifdef, defines)

            filetext = filetext.replace(ifdef, newifdef)

    # запись в файл кода без лишних блоков ifdef/ifndef
    fileopen.close()
    fileopen = open(file, "w")

    # убираем лишние отступы
    filetext = re.sub(r"\n{3,}", "\n\n", filetext)

    fileopen.write(filetext)
    fileopen.close()


# ф-я проверяющая 1 блок ifdef/ifndef
def ifblockprocessing(blockstr, defines):

    # списки условных деректив блока
    ifdef = re.search(r"`(?:ifndef|ifdef) +\w+\n", blockstr)[0]
    elsifs = re.findall(r"`elsif +\w+\n", blockstr)
    else_ = re.search(r"`else", blockstr)

    if else_ != None:
        else_ = else_[0]

    # сравниваем макросы ifdef/ifndef с define
    for define in defines:
        if define in ifdef:
            # если нашли совпадение с define и мы обрабатываем ifdef, то возвращаем код блока
            if "ifdef" in ifdef:
                blockstr = cleanblock(blockstr, ifdef)
                return blockstr
            # если нашли совпадение с define и мы обрабатываем ifndef
            else:
                return ""  # возращаем пустоту (т.е. блок ifndef удалится)

    # если совпадений с define не было найдено и мы обрабатываем ifndef, то
    # возращаем код блока
    if "ifndef" in ifdef:
        blockstr = cleanblock(blockstr, ifdef)
        return blockstr

    # сравниваем elsif с define
    for define in defines:
        for elsif in elsifs:
            if define in elsif:
                # если нашли совпадение, то возвращаем код блока elsif
                blockstr = cleanblock(blockstr, elsif)
                return blockstr

    # отдаем блок с else
    if else_:
        blockstr = cleanblock(blockstr, else_)
        return blockstr

    # если не нашли никаких совпадений, возвращаем пустоту
    return ""


# ф-я возвращающая внутренний код блока
def cleanblock(block, face):
    blockwithface = re.search(face + r"[\s|\S]*?`elsif", block)
    if blockwithface != None:  # если блок с elsif концом
        blockwithface = blockwithface[0]
        blockwithface = re.sub(face, '', blockwithface)
        blockwithface = re.sub("`elsif", '', blockwithface)
    else:
        blockwithface = re.search(face + r"[\s|\S]*?`else", block)
        if blockwithface != None:  # если блок с else концом
            blockwithface = blockwithface[0]
            blockwithface = re.sub(face, '', blockwithface)
            blockwithface = re.sub("`else", '', blockwithface)
        else:  # если блок с endif концом
            blockwithface = re.search(face + r"[\s|\S]*?`endif", block)
            blockwithface = blockwithface[0]
            blockwithface = re.sub(face, '', blockwithface)
            blockwithface = re.sub("`endif", '', blockwithface)

    return blockwithface




