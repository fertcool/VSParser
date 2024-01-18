
from work_with_files import *

# ------------------------------ОСНОВНЫЕ_ФУНКЦИИ------------------------------ #
# ф-я запускающая удаление либо во всем проекте либо в 1 файле
def deletecomments(patterns, plus = False):
    from erase_comments import json_struct
    # удаление комментариев по всему проекту
    if json_struct["conf"]["allfiles"]:

        # получение списка путей к файлам sv
        svfiles = get_sv_files(os.curdir)

        # цикл по всем файлам
        for sv in svfiles:

            # удаление комментариев по текущему sv файлу
            delete(sv, patterns, plus)

    # если необходимо обработать только 1 файл
    else:

        # удаление комментариев по нужному sv файлу
        delete(json_struct["conf"]["filename"], patterns, plus)


# удаление комментариев по заданному списку шаблонов
def delete(svfile, patterns, plus):

    svtext = get_file_text(svfile)  # текст кода sv

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
               svtext = svtext.replace(com, '\n')

    # если работаем с minus списком
    else:
        # ищем удаляемые комментарии
        for pattern in patterns:
            if re.findall(pattern, svtext):

                # удаляем комментарий, совпавший с шаблоном
                svtext = re.sub(pattern, '\n', svtext)

    # удаялем лишние отступы
    svtext = delete_indents(svtext)

    # запись в файл текста кода без комментариев
    write_text_to_file(svfile, svtext)




