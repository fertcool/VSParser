import os
import re
import json
import scanfiles

# ф-я запускающая удаление комментариев sv файлов
def launch():
    json_file = open(r"erase_comments.json", "r")
    json_struct = json.load(json_file)

    # удаление комментариев вида // и /**/
    if json_struct["tasks"]["a"]:
        BasePatterns = ["/\*[\s|\S]*?\*/", "//[^\n]*\n"]
        deletecomments(json_struct, BasePatterns)

    #удаление комментариев без основных ascii символов
    if json_struct["tasks"]["b"]:
        asciipatterns = ["/\*[ -~\n]*?\*/", "//[ -~]*\n"]
        deletecomments(json_struct, asciipatterns, True)

    # удаление комментариев по minus списку
    if json_struct["tasks"]["c"]:
        minus = json_struct["minus"]
        deletecomments(json_struct, minus)

    # удаление комментариев по plus списку
    if json_struct["tasks"]["d"]:
        deletecomments(json_struct, json_struct["plus"], True)


# ф-я запускающая удаление либо во всем проекте либо в 1 файле
def deletecomments(json, patterns, plus = False):

    # удаление комментариев по всему проекту
    if json["conf"]["allfiles"]:

        # получение списка путей к файлам sv
        svfiles = scanfiles.getsv(os.curdir)

        # цикл по всем файлам
        for sv in svfiles:

            # удаление комментариев по текущему sv файлу
            delete(sv, patterns, plus)

    # если необходимо обработать только 1 файл
    else:

        # удаление комментариев по нужному sv файлу
        delete(json["conf"]["filename"], patterns, plus)


# удаление комментариев по заданному списку шаблонов
def delete(svfile, patterns, plus):
    file = open(svfile, "r")
    svtext = file.read()  # текст кода sv

    # если работаем с plus списком
    if plus:
        comments = []  # список всех комментариев
        BasePatterns = ["/\*[\s|\S]*?\*/", "//[^\n]*\n"]

        # поиск всех комментариев
        for pattern in BasePatterns:
            comments.extend(re.findall(pattern, svtext))

        # цикл по каждому комментарию
        for com in comments:
            match = False  # флаг совпадения с положительным шаблоном

            # поиск совпадения
            for pluspattern in patterns:
                if(re.match(pluspattern, com)):
                    match = True

            # если совпадений нет то удаляем комментарий
            if not match:
               svtext = svtext.replace(com, '')

    # если работаем с minus списком
    else:
        # ищем удаляемые комментарии
        for pattern in patterns:
            if re.findall(pattern, svtext):
                print(re.findall(pattern, svtext))

                # удаляем комментарий, совпавший с шаблоном
                svtext = re.sub(pattern, '', svtext)
    file.close()
    file = open(svfile, "w")

    # запись в файл текста кода без комментариев
    file.write(svtext)
    file.close()



