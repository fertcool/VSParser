from work_with_files import *

# ------------------------------¬—ѕќћќ√ј“≈Ћ№Ќџ≈_‘”Ќ ÷»»------------------------------ #

# ф-€ получени€ списка всех instance обьектов по словарю модулей (в круглых скобках - тип обьекта)
def get_inst_list(insts_in_modules_dict):

    insts = []  # список instance обьектов

    # цикл добавлени€ instance обьектов из словар€ в список
    for module in insts_in_modules_dict:
        insts += insts_in_modules_dict[module]

    return insts


# ф-€ создани€ словар€ модулей (ключ - название модул€,
# значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))
def get_insts_in_modules():
    from read_hierarchy import files, modules

    insts_in_modules_dict = {}  # словарь модулей

    # цикл порлучени€ instance обьектов каждого файла
    for file in files:

        filetext = get_file_text(file)  # текст файла

        # список полных текстов блоков модулей файла
        moduleblocks = get_module_blocks(filetext)

        # цикл поиска instance обьектов во всех модул€х файла
        for moduleblock in moduleblocks:

            modulename = re.search(r"module +(\w+)", moduleblock)[1]  # им€ модул€

            insts_in_modules_dict[modulename] = []  # инициализируем список instance обьектов модул€

            # цикл поиска instance модул€ module из списка modules в файле
            for module in modules:

                # поиск
                searched_instance = re.findall(r"(?<!module)[ \n]+" + module + r"[ \n]+(\w+)[ \n]*\([\w|\W]*?\) *;", moduleblock)
                searched_instance += re.findall(r"(?<!module)[ \n]+" + module + r"[ \n]+#\([\w|\W]*?\)[ \n]*(\w+)[ \n]*\([\w|\W]*?\) *;", moduleblock)

                # добавление в список с типом в круглых скобках
                if searched_instance:
                    for inst in searched_instance:
                        insts_in_modules_dict[modulename].append(inst + "(" + module + ")")

                # если instance обьектов нет - продолжаем поиск
                else:
                    continue

    return insts_in_modules_dict