
from work_with_files import *
# ------------------------------ФУНКЦИИ_ПОИСКА_ИДЕНТИФИКАТОРОВ----------------------------- #

# возращает имена всех instance обьектов
def search_instances(text):

    # все модули и их порты
    modules = get_all_modules()

    instances = []  # список instance обьектов

    # цикл поиска instance модуля module из списка modules в файле
    for module in modules:

        # поиск
        searched_instance = re.findall(r"(?<!module)[ \n]+" + module + r"[ \n]+(\w+)[ \n]*\([\w|\W]*?\) *;", text)
        searched_instance += re.findall(
            r"(?<!module)[ \n]+" + module + r"[ \n]+#\([\w|\W]*?\)[ \n]*(\w+)[ \n]*\([\w|\W]*?\) *;", text)

        # добавление в список
        if searched_instance:
            instances += searched_instance
        else:
            continue

    # возврат списка имен instance
    return instances


# возращает блоки текстов всех instance обьектов
def search_instance_blocks(text):

    # все модули
    modules = get_all_modules()

    instance_blocks = []  # список instance обьектов

    # цикл поиска instance модуля module из списка modules в файле
    for module in modules:

        # поиск
        searched_instance = re.findall(r"(?<!module)[ \n]+(" + module + r"[ \n]+\w+[ \n]*\([\w|\W]*?\) *;)", text)
        searched_instance += re.findall(
            r"(?<!module)[ \n]+(" + module + r"[ \n]+#\([\w|\W]*?\)[ \n]*\w+[ \n]*\([\w|\W]*?\) *;)", text)

        # добавление в список
        if searched_instance:
            instance_blocks += searched_instance
        else:
            continue

    # возврат списка имен instance
    return instance_blocks


# ф-я поиска портов input/output/inout в тексте
def search_inouts(text):
    inouts = base_ind_search(text, ["(?:input|output|inout)"])  # список input/output/inout портов

    return inouts


# ф-я возвращающая список обычных строчных (без структур) идентификаторов в тексте
def base_ind_search(text, ind_list):
    base_ind_pattern = ind_list[0]

    # начало регулярного выражения для нахождения хотябы одного из идентификаторов
    if len(ind_list) > 1:
        base_ind_pattern = "(?:"
        for ind in ind_list:
            base_ind_pattern += ind + "|"
        base_ind_pattern = base_ind_pattern[:-1]
        base_ind_pattern += ")"

    # список строк с определением или инициализацией базовых идентификаторов
    # в группе хранятся списки идентификаторов
    base = []
    # список строк с информацией после типа идентификатора
    baseindentif = re.findall(r"\W" + base_ind_pattern + " +(.*?[,;)=])", text)

    # поиск строк со множественным определением
    baseindentif += re.findall(r"\W" + base_ind_pattern + " +.*?,(.*?;)", text)

    # поиск строк с \n в конце
    baseindentif += re.findall(r"\W" + base_ind_pattern + " +([^;,)=\n]+?\n)", text)

    # выделение самих идентификаторов из списка baseindentif
    for i in range(len(baseindentif)):
        base += re.findall(r"(\w+) *[,;)=\n]", baseindentif[i])

        # выделение идентификаторов, у которпых в конце [\d:\d]
        base += re.findall(r"(\w+) +\[[\d :\-*\w`]+] *[,;=\n]", baseindentif[i])

    return base


# ф-я возвращающая список идентификаторов, связанных с enum
def enum_ind_search(text):
    enums = []  # список идентифиакторов внутри блока enums и самих идентификатров определяемых enums

    # список строк с блоками enums
    # в 1 группе хранится текст внутри блока
    # во 2 группе хранятся идентификаторы enums
    enumblocks = re.findall(r"\Wenum[\w,; \[\]`:-]+\{([\w|\W]+?)} *([\w,; \[\]`:-]+)", text)

    # цикл обработки enums (выделения идентификаторов из текстов enums)
    for i in range(len(enumblocks)):
        insideWOeq = re.sub(r"=[ \w']+", '', enumblocks[i][0])  # текст внутри блока без присваиваний
        insideind = re.findall(r"(\w+) *", insideWOeq)  # список идентификаторов внутри блока
        outsideind = re.findall(r"(\w+) *",
                                enumblocks[i][1])  # список идентификаторов снаружи блока (объекты enum)
        enumblocks[i] = (insideind + outsideind)
        enums += enumblocks[i]  # в итоге делаем список всех идентификаторов связанных с блоками enum

    return enums