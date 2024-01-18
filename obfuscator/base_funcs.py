
from obfuscator.encode import encrypt_file, write_decrt_in_file, encrypt_text, regexp_to_str
from obfuscator.search_inds import search_instances, search_inouts, base_ind_search, enum_ind_search
from obfuscator.utilities import *


# ------------------------------ОСНОВНЫЕ_ФУНКЦИИ------------------------------ #

# ф-я обфускации текста в пределах `pragma protect on - `pragma protect off
def ind_search_and_replace_protect(file):

    filetext = get_file_text(file)  # текст файла

    # текст обрабатываемого блока кода
    protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

    if protectblocks:
        # обработка ifdef/ifndef
        preobfuscator_ifdef(file)

        filetext = get_file_text(file)  # текст всего файла после обработки ifdef/ifndef

        # повторяем поиск, т.к. провели обработку ifdef/ifndef
        protectblocks = re.findall(r"`pragma protect on([\w|\W]+?)`pragma protect off", filetext)

        # цикл обработки блоков кода
        for protectblock in protectblocks:
            filetext = get_file_text(file)  # текст всего файла после обработки ifdef/ifndef

            # запись в файл текста protect блока
            write_text_to_file(file, protectblock)

            # заменяем все идентификаторы в protect блоке
            allind_search_and_replace(file)

            # чтение нового текста модуля из файла
            newprotectblock = get_file_text(file)

            # запись в файл текста с обработанным protect блоком
            write_text_to_file(file, filetext.replace("`pragma protect on" + protectblock
                                                                      + "`pragma protect off", newprotectblock))

    else:
        return


# ф-я поиска и замены любых идентификаторов, кроме input/output/inout в заданном модуле
def module_search_and_replace_wo_inout(file, module):
    filetext = get_file_text(file)  # текст файла

    moduleblock = get_module_blocks(filetext, module)

    # если нашли модуль, то обрабатываем его
    if moduleblock:

        # обработка ifdef/ifndef
        preobfuscator_ifdef(file)

        moduletext = get_module_blocks(filetext, module)  # текст блока модуля

        # instance идентификаторы (имена)
        instances = search_instances(moduletext)

        # шифруем блоки instance, чтобы они не участвовали далее в обрвботке
        decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

        filetext = get_file_text(file)  # текст файла после шифровки instance обьектов
        newmoduletext = get_module_blocks(filetext, module)  # текст модуля после
        # шифровки instance обьектов

        inouts = search_inouts(newmoduletext)  # список всех input/output/inout идентификаторов

        defines = re.findall(r"`define +(\w+)", newmoduletext)  # список идентификаторов define

        # список строк с определением или инициализацией базовых идентификаторов
        # в группе хранятся списки идентификаторов
        base = base_ind_search(newmoduletext, ["wire", "reg", "parameter", "localparam", "byte", "shortint",
                                               "int", "integer", "longint", "bit", "logic", "shortreal",
                                               "real", "realtime", "time", "event"])

        enums = enum_ind_search(newmoduletext)  # идентификаторы enums

        structs = re.findall(r"\Wstruct[\w|\W]+?} *(\w+);", newmoduletext)  # список идентификаторов struct

        typedefs = re.findall(r"\Wtypedef[\w|\W]+?} *(\w+);", newmoduletext)  # список идентификаторов typedef

        # удаление повторных идентификаторов typedef из enums и struct
        for a in structs:
            if a in typedefs:
                structs.remove(a)
        for a in enums:
            if a in typedefs:
                enums.remove(a)

        # поиск идентификаторов, типа typedef'ов
        for typedef in typedefs:
            base_typedef = re.findall(typedef + r" +(.*?[,;\n)=])", newmoduletext)
            for i in range(len(base_typedef)):
                base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # добавление найденных идентификаторов в base

        # поиск идентификаторов модулей и функций
        funcs = re.findall(r"(?:task|function) +[\w|\W]+?(\w+)[ \n]*(?:\(|#\(|;)", filetext)

        # все идентификаторы (без повторов)
        allind = set(defines + base + enums + structs + typedefs + funcs + instances)

        # удаление из списка allind найденных input/output/inout идентификаторов
        delete_inouts(inouts, allind)

        # шифровка идентификаторов и создание таблицы соответствия в модуле
        decrypt_table = {}
        encrypt_file(allind, file, newmoduletext, decrypt_table)

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

        # проверяем есть ли в модуле параметры
        modules_wp = re.findall(r"\Wparameter\W",
                                newmoduletext)
        newfiletext = get_file_text(file)  # текст файла после шифрации некоторых идентификаторов

        # дешифруем instance блоки (перед шифрацией instance блоков в других файлах,
        # т.к. они могут быть в самом файле с описанием модулей,
        # и соответственно в самом файле тоже нажо поменять порты и названия instance обьектов)
        for decr_inst in decrypt_table_instances:
            newfiletext = newfiletext.replace(decr_inst, decrypt_table_instances[decr_inst])
        # соответственно записываем зашифрованный текст с расшифрованными instance олбьектами в файл
        write_text_to_file(file, newfiletext)

        # если модуль оказался с параметрами, то заменяем их в других файлах
        if modules_wp:
            # заменяем все instance блоки в других файлах (именно параметры)
            # функции отдаем имя модуля
            change_instances_ports_allf([module], inv_decrypt_table)

        # чтение нового текста из файла после изменения instance блоков во всех файлах
        newfiletext = get_file_text(file)

        # заменяем идентификаторы instance
        for inst in instances:
            newfiletext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", newfiletext)

        # создаем файл с таблицей соответствия
        write_decrt_in_file(file, decrypt_table)

        # запись в файл текст с обработанным блоком module
        write_text_to_file(file, newfiletext)

    else:
        print(module + " in " + file + " not found")
        return


# ф-я поиска и замены выбранного вида идентификаторов (input/output/inout, wire, reg, module, instance, parameter)
def ind_search_and_replace(file, ind):
    # обработка ifdef/ifndef
    preobfuscator_ifdef(file)

    # шифруем блоки instance, чтобы они не участвовали далее в обработке
    decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

    filetext = get_file_text(file)  # текст файла

    decrypt_table = {}  # таблица соответствия для замененных идентификаторов

    allind = []  # список всех идентификаторов

    # коррекция
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # если выбранный тип идентификатора - "базовый", то проводим соответствующий поиск
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        # поиск всех идентификаторов типа ind
        allind = base_ind_search(filetext, [ind])

        # обрабатываем не порты
        if ind != "(?:input|output|inout)":

            # обрабатываем parameter
            if ind == "parameter":

                # ищем модули с параметрами
                modules_with_par = []
                module_blocks = get_module_blocks(filetext)  # список модулей, описанных в тексте файла
                for module_block in module_blocks:
                    if re.search(r"\Wparameter\W", module_block):
                        modules_with_par.append(re.search(r"module +(\w+)", module_block)[1])

                # шифровка идентификаторов
                encrypt_file(allind, file, filetext, decrypt_table)

                filetext = get_file_text(file)  # текст файла после шифрации модулей

                # дешифруем instance блоки (перед шифрацией instance блоков в других файлах,
                # т.к. они могут быть в самом файле с описанием модулей,
                # и соответственно в самом файле тоже нажо поменять порты и названия instance обьектов)
                for decr_inst in decrypt_table_instances:
                    filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])
                # соответственно записываем зашифрованный текст с расшифрованными instance олбьектами в файл
                write_text_to_file(file, filetext)

                # если нашли модули с параметрами, то заменяем их в других файлах
                if modules_with_par:
                    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

                    # заменяем все instance блоки в других файлах (именно параметры)
                    change_instances_ports_allf(modules_with_par, inv_decrypt_table)

                # создаем файл с таблицей соответствия
                write_decrt_in_file(file, decrypt_table)

            # обрабатываем reg, wire
            else:
                inouts = search_inouts(filetext)

                if ind == "wire":  # добавляем структуры wire
                    allind += re.findall(r"wire +struct[\w :\[\]\-`]*?\{[\w|\W]*?} *(\w+)[,;\n)=]", filetext)

                # удаляем input/output/inout порты из allind
                delete_inouts(inouts, allind)

                # шифровка идентификаторов и создание таблицы соответствия
                encrypt_file(allind, file, filetext, decrypt_table)

                filetext = get_file_text(file)  # текст файла после шифрации

                # дешифруем instance блоки
                for decr_inst in decrypt_table_instances:
                    filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

                write_text_to_file(file, filetext)
                write_decrt_in_file(file, decrypt_table)

        # если обрабатываем input/output/inout порты, то надо в других файлах обработать порты instance
        # обьектов соответсвующих модулей
        else:
            modules = get_modules(filetext)  # список модулей, описанных в тексте файла

            # шифровка идентификаторов
            encrypt_file(allind, file, filetext, decrypt_table)

            filetext = get_file_text(file)  # текст файла после шифрации модулей

            inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

            # дешифруем instance блоки (перед шифрацией instance блоков в других файлах,
            # т.к. они могут быть в самом файле с описанием модулей,
            # и соответственно в самом файле тоже нажо поменять порты и названия instance обьектов)
            for decr_inst in decrypt_table_instances:
                filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])
            # соответственно записываем зашифрованный текст с расшифрованными instance олбьектами в файл
            write_text_to_file(file, filetext)

            # заменяем все instance блоки в других файлах, тк мы изменили названия портов функций modules
            change_instances_ports_allf(modules, inv_decrypt_table)

            # создаем файл с таблицей соответствия
            write_decrt_in_file(file, decrypt_table)

    # если выбранный тип идентификатора module - то заменяем идентификаторы модулей и тип
    # instance обьектов в других файлах
    elif ind == "module":

        # поиск идентификаторов модулей
        allind = get_modules(filetext)

        # шифровка идентификаторов
        encrypt_file(allind, file, filetext, decrypt_table)

        filetext = get_file_text(file)  # текст файла после шифрации модулей

        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

        # дешифруем instance блоки (перед шифрацией instance блоков в других файлах,
        # т.к. они могут быть в самом файле с описанием модулей,
        # и соответственно в самом файле тоже нажо поменять порты и названия instance обьектов)
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])
        # соответственно записываем зашифрованный текст с расшифрованными instance олбьектами в файл
        write_text_to_file(file, filetext)

        # заменяем все типы instance блоков в других файлах
        change_instances_ports_allf(allind, inv_decrypt_table)

        # создаем файл с таблицей соответствия
        write_decrt_in_file(file, decrypt_table)

    # замена instance идентификаторов
    elif ind == "instance":

        # дешифруем instance блоки
        for decr_inst in decrypt_table_instances:
            filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])

        # поиск всех instance идентификаторов
        allind = search_instances(filetext)

        # шифровка instance идентификаторов и создание таблицы соответствия
        encrypt_text(allind, "", decrypt_table)
        inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия
        for inst in allind:
            filetext = re.sub(inst + r" *\(", inv_decrypt_table[inst] + "(", filetext)

        # запись обфусцированного текста
        write_text_to_file(file, filetext)

        write_decrt_in_file(file, decrypt_table)

    # ошибка
    else:
        print("literal not correct")
        return


# ф-я поиска и замены любых идентификаторов
def allind_search_and_replace(file):

    # обработка ifdef/ifndef
    preobfuscator_ifdef(file)

    filetext = get_file_text(file)  # текст файла

    # instance идентификаторы (имена)
    instances = search_instances(filetext)

    # шифруем блоки instance, чтобы они не участвовали далее в обрвботке
    decrypt_table_instances = preobfuscator_instance(file)  # таблица дешифрации блоков instance

    filetext = get_file_text(file)  # текст файла после ifdef обработки и шифровки instance обьектов

    modules = get_modules(filetext)  # список модулей, описанных в тексте файла

    defines = re.findall(r"`define +(\w+)", filetext)  # список идентификаторов define

    # список строк с определением или инициализацией базовых идентификаторов
    # в группе хранятся списки идентификаторов
    base = base_ind_search(filetext, ["input", "output", "inout", "wire", "reg",
                                      "parameter", "localparam", "byte", "shortint",
                                      "int", "integer", "longint", "bit", "logic", "shortreal",
                                      "real", "realtime", "time", "event"])

    enums = enum_ind_search(filetext)  # список идентификаторов enums

    structs = re.findall(r"\Wstruct[\w|\W]+?} *(\w+);", filetext)  # список идентификаторов struct

    typedefs = re.findall(r"\Wtypedef[\w|\W]+?} *(\w+);", filetext)  # список идентификаторов typedef

    # удаление повторных идентификаторов typedef из enums и struct
    for a in structs:
        if a in typedefs:
            structs.remove(a)
    for a in enums:
        if a in typedefs:
            enums.remove(a)

    # поиск идентификаторов, типа typedef'ов
    for typedef in typedefs:
        base_typedef = re.findall(typedef + r" +(.*?[,;\n)=])", filetext)
        for i in range(len(base_typedef)):
            base += re.findall(r"(\w+) *[,;\n)=]", base_typedef[i])  # добавление найденных идентификаторов в base

    # поиск идентификаторов модулей и функций
    funcs = re.findall(r"(?:task|function) +[\w|\W]+?(\w+)[ \n]*(?:\(|#\(|;)", filetext)

    # все идентификаторы (без повторов)
    allind = set(defines + base + enums + structs + typedefs + modules + funcs + instances)  # все идентификаторы

    # шифровка идентификаторов и создание таблицы соответствия
    decrypt_table = {}
    encrypt_file(allind, file, filetext, decrypt_table)

    filetext = get_file_text(file)  # текст файла после шифрации части идентификаторов

    inv_decrypt_table = {v: k for k, v in decrypt_table.items()}  # перевернутая таблица соответствия

    # дешифруем instance блоки (перед шифрацией instance блоков в других файлах,
    # т.к. они могут быть в самом файле с описанием модулей,
    # и соответственно в самом файле тоже нажо поменять порты и названия instance обьектов)
    for decr_inst in decrypt_table_instances:
        filetext = filetext.replace(decr_inst, decrypt_table_instances[decr_inst])
    # соответственно записываем зашифрованный текст с расшифрованными instance олбьектами в файл
    write_text_to_file(file, filetext)

    # заменяем все instance блоки в других файлах, тк мы изменили названия портов функций modules
    change_instances_ports_allf(modules, inv_decrypt_table)

    filetext = get_file_text(file)  # текст файла после изменения instance блоков во всех файлах

    # создаем файл с таблицей соответствия
    write_decrt_in_file(file, decrypt_table)

    # шифруем входные данные портов instance блока
    for invdt in inv_decrypt_table:
        ports = set(re.findall(r"\( *" + invdt + r"\W", filetext))
        for port in ports:
            # заменяем некоторые симвылы для правильной задачи регулярного выражения
            port = regexp_to_str(port)

            filetext = re.sub(port, "(" + inv_decrypt_table[re.search(r"\w+", port)[0]] + port[-1], filetext)

    # заменяем идентификаторы instance
    for inst in instances:
        filetext = re.sub(inst + r"[ \n]*\(", inv_decrypt_table[inst] + "(", filetext)

    # запись обфусцированного текста
    write_text_to_file(file, filetext)


# ф-я замены названий портов instance обьектов, их и типов во всех файлах проекта
def change_instances_ports_allf(modules, decr_table):
    files = get_sv_files(os.curdir)  # все файлы

    # цикл изменения портов во всех файлах
    for file in files:

        # обрабатываем ifdef/ifndef
        preobfuscator_ifdef(file)

        decrypt_table_instances = {}  # таблица соответствия портов instance обьекта

        filetext = get_file_text(file)  # текст файла

        # цикл обработки instance обьектов модулей modules
        for module in modules:

            # находим все instance обьекты (их текст)
            # instances = search_instance_blocks(filetext)
            instances = re.findall(r"(?<!module)[ \n]+(" + module + r"[ \n]+\w+[ \n]*\([\w|\W]*?\) *;)", filetext)
            instances += re.findall(
                r"(?<!module)[ \n]+(" + module + r"[ \n]+#\([\w|\W]*?\)[ \n]*\w+[ \n]*\([\w|\W]*?\) *;)", filetext)

            # если такие обьекты существуют, то обрабатываем их
            if instances:

                # цикл обработки кажого обьекта instance
                for instance in instances:

                    # сохраняем старый текст обьекта
                    oldinstance = instance

                    # поиск всех портов обьекта
                    inouts = re.findall(r"\.(\w+)", instance)

                    # цикл замены названия портов на соответствующие в таблице decr_table
                    for inout in inouts:
                        if inout in decr_table:
                            port = re.search(r"\."+inout+r"\W", instance)[0]
                            instance = instance.replace(port, "." + decr_table[inout] + port[-1])

                            # добавляем в таблицу decrypt_table_instances соответствующую замену из decr_table
                            decrypt_table_instances[decr_table[inout]] = inout

                    # если необходимо - заменяем название модуля instance обьекта и добавляем в таблицу
                    # decrypt_table_instances
                    if module in decr_table:
                        instance = re.sub(module, decr_table[module], instance, 1)  # заменяем только 1 вхождение
                        decrypt_table_instances[decr_table[module]] = module

                    # заменяем текст на измененный
                    filetext = filetext.replace(oldinstance, instance)

            # если таких обьектов нет, то продолжаем поиск
            else:
                continue
        # если таблица decrypt_table_instances не пуста, то записываем ее в файл таблиц соответствия
        if decrypt_table_instances:
            write_decrt_in_file(file, decrypt_table_instances)

        # запись измененного текста в файл
        write_text_to_file(file, filetext)