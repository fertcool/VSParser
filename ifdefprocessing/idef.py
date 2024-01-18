import erase_comments
from work_with_files import *

# ------------------------------‘”Ќ ÷»»_IFDEF/IFNDEF_ќЅ–јЅќ“ »------------------------------ #


# ф-€ ifdef/ifndef обработки файла
def ifdef_pr_forfile(file):
    from ifdefprocessing import json_struct
    #  удал€ем комментарии с определени€ми
    erase_comments.delete(file, [r"/\* *`define *[\s|\S]*?\*/", r"// *`define *[^\n]*\n"], False)

    filetext = get_file_text(file)  # текст файла

    # цикл пока есть блоки ifdef или ifndef в файле
    while (re.search(r"`(?:ifndef|ifdef)[\s|\S]*?`endif", filetext)):

        # поиск всех блоков ifdef/ifndef (возможно с вложени€ми)
        ifdefs = re.findall(r"`(?:ifndef|ifdef)[\s|\S]*?`endif", filetext)

        # убираем вложени€, если они есть (например ifdef...ifdef...endif -> ifdef...endif)
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
            defines.extend(json_struct["defines"])  # добавл€ем внешние define
            # оставл€ем только названи€ define
            for i in range(len(defines)):
                defines[i] = re.sub("`define +", '', defines[i])
                defines[i] = re.sub("\n", '', defines[i])

            # обработка блока
            newifdef = ifblockprocessing(ifdef, defines)

            # записываем обработанный текст в файл
            filetext = filetext.replace(ifdef, newifdef)

    # уда€лем лишние отступы
    filetext = delete_indents(filetext)

    # запись в файл кода без лишних блоков ifdef/ifndef
    write_text_to_file(file, filetext)


# ф-€ провер€юща€ 1 блок ifdef/ifndef
def ifblockprocessing(blockstr, defines):

    # списки условных деректив блока
    ifdef = re.search(r"`(?:ifndef|ifdef) +\w+\n", blockstr)[0]
    elsifs = re.findall(r"`elsif +\w+\n", blockstr)
    else_ = re.search(r"`else", blockstr)

    if else_:
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
                return ""  # возращаем пустоту (т.е. блок ifndef удалитс€)

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


# ф-€ возвращающа€ внутренний код блока
def cleanblock(block, face):

    blockwithface = re.search(face + r"[\s|\S]*?`elsif", block)

    if blockwithface:  # если блок с elsif концом
        blockwithface = blockwithface[0]
        blockwithface = re.sub(face, '', blockwithface)
        blockwithface = re.sub("`elsif", '', blockwithface)
    else:

        blockwithface = re.search(face + r"[\s|\S]*?`else", block)

        if blockwithface:  # если блок с else концом
            blockwithface = blockwithface[0]
            blockwithface = re.sub(face, '', blockwithface)
            blockwithface = re.sub("`else", '', blockwithface)

        else:  # если блок с endif концом
            blockwithface = re.search(face + r"[\s|\S]*?`endif", block)
            blockwithface = blockwithface[0]
            blockwithface = re.sub(face, '', blockwithface)
            blockwithface = re.sub("`endif", '', blockwithface)

    return blockwithface