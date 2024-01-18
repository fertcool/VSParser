import obfuscator
from obfuscator.deobfuscator.utilities import *
from work_with_files import *
# ------------------------------ОСНОВНЫЕ_ФУНКЦИИ------------------------------ #

# функция деобфускации всех идентификаторов в файле
def decryptall(file):

    filetext = get_file_text(file)  # текст файла

    # ищем все порты и параметры модулей в файле, чтобы далее расшифровать их во всех файлах
    ports = obfuscator.base_ind_search(filetext, ["input", "output", "inout", "parameter"])

    modules = get_modules(filetext)  # список модулей, описанных в тексте файла

    # получаем таблицу соответствия
    decrypt_table = get_decrt_in_file(file)

    # цикл замены идентификаторов согласно таблице соответствия
    for ident in decrypt_table:
        filetext = re.sub(ident, decrypt_table[ident], filetext)

    # расшифвровываем порты, имена модулей, параметры во всех файлах проекта
    change_ind_allf(modules+ports)

    # запись нового текста в файл
    write_text_to_file(file, filetext)


# ф-я деобфускации выбранного вида идентификаторов (input/output/inout, wire, reg, module, instance, parameter)
def decrypt_one_ind(file, ind):

    filetext = get_file_text(file)  # текст файла

    decrypt_table = get_decrt_in_file(file)  # таблица соответствия

    allind = []  # список всех идентификаторов

    # коррекция
    if ind == "input/output/inout":
        ind = "(?:input|output|inout)"

    # если выбранный тип идентификатора - базовый, то проводим соответствующий поиск
    if ind == "(?:input|output|inout)" or ind == "wire" or ind == "reg" or ind == "parameter":

        inouts = obfuscator.search_inouts(filetext)  # список всех input/output/inout идентификаторов

        # поиск всех input/output/inout идентификаторов
        if ind != "(?:input|output|inout)":

            # поиск всех строк с идентификаторами класса ind
            allind = obfuscator.base_ind_search(filetext, [ind])

            if ind == "wire":  # добавляем структуры wire
                allind += re.findall(r"wire +struct[\w :\[\]\-`]*?\{[\w|\W]*?} *(\w+)[,;\n)=]", filetext)

            # удаление из списка allind найденных input/output/inout идентификаторов
            obfuscator.delete_inouts(inouts, allind)

        else:

            allind = inouts

    # если выбранный тип идентификатора - module или instance, то проводим соответствующий поиск
    elif ind == "module":

        # поиск идентификаторов модулей
        allind = get_modules(filetext)

    elif ind == "instance":

        allind = obfuscator.search_instances(filetext)

    # ошибка
    else:
        print("literal not correct")
        return

    # замена выбранного класса идентификаторов
    for indef in allind:
        if indef in decrypt_table:
            filetext = re.sub(indef, decrypt_table[indef], filetext)

    # замена расшифврованных портов и паараметров во всех файлах
    if ind == "module" or ind == "(?:input|output|inout)" or ind == "parameter":
        change_ind_allf(allind)

    # запись нового текста в файл
    write_text_to_file(file, filetext)


# ф-я деобфускации идентификаторов input/output/inout выбранного модуля
def decrypt_module_inout(file, module):

    filetext = get_file_text(file)  # текст файла

    decrypt_table = get_decrt_in_file(file)  # таблица соответствия

    # ищем текст модуля
    moduleblock = get_module_blocks(filetext, module)

    # если нашли модуль
    if moduleblock:

        moduletext = moduleblock  # текст блока модуля

        # ищем порты модуля
        inouts = obfuscator.search_inouts(moduletext)

        # замена выбранного класса идентификаторов
        for ind in inouts:
            if ind in decrypt_table:
                filetext = re.sub(ind, decrypt_table[ind], filetext)

        # запись нового текста в файл
        write_text_to_file(file, filetext)

        # заменяем порты в других файлах
        change_ind_allf(inouts)

    # ошибка
    else:
        print(module + " in " + file + " not found")
        return