from work_with_files import *

# ------------------------------ФУНКЦИИ_РАБОТЫ_С_INCLUDE_ФАЙЛАМИ------------------------------ #


# ф-я добавляющая в текст sv файла include файлы (в том числе включая include включаемого файла)
def addincludes(filetext, included = None):
    from ifdefprocessing import json_struct
    if included is None:
        included = []

    # поиск всех include в файле (расположенных последовательно)
    includes = re.findall(r"`include *\"([\w\.]+)\"", filetext)

    # цикл по всем включаемым файлам
    for include in includes:
        existfile = False  # флаг существования включаемого файла

        # цикл по всем директориям, где должны хранится include файлы
        for includepath in json_struct["includes"]:

            # если файл в текущей директоии есть (и он еще не был включен)
            # , то добавляем текст включаемого файла
            if os.path.exists(includepath+"\\"+include) and include not in included:

                existfile = True  # флаг существования файла

                includetext = get_file_text(includepath+"\\"+include)  # текст включаемого файла

                # вставляем в файл на место 1 включения
                filetext = re.sub("`include *\""+include+"\"", includetext, filetext, 1)

                # удаление повторяющихся включений
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                  filetext)

                # добавляем вставленный файл в список включенных
                included.append(include)

                # заново просматриваем файл (ищем снова включения)
                filetext = addincludes(filetext, included)

                # выходим, т.к. уже нашли и вставили файл
                break

        # если включаемый файл не был найден, то оставляем соответствующую пометку и идем к следующему файлу
        if not existfile:

            # добавляем пометку
            if include not in included:  # если файл не был включен
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file don't exist",
                                  filetext)
            else:  # если файл был включен
                filetext = re.sub("`include *\"" + include + "\"", "//include \"" + include + "\" file already include",
                                  filetext)
            continue

    return filetext


# ф-я добавления всех include файлов для 1 файла
def include_for_file(file):

    filetext = get_file_text(file)  # текст файла

    # изменяем текст sv файла - заменяем `include на текст соответствующего файла
    filetext = addincludes(filetext)

    write_text_to_file(file, filetext)  # запись нового текста в файл