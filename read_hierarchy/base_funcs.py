
from read_hierarchy.search_report import *

# ------------------------------ОСНОВНЫЕ_ФУНКЦИИ------------------------------ #

# ф-я запуска восстановления структуры вызовов модулей
def restoring_call_structure():
    from read_hierarchy import json_struct
    inst_in_modules_dict = get_insts_in_modules()  # словарь модулей (ключ - название модуля,
    # значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))

    # запись в файл отчета структуры вызовов модулей
    project_struct_report(json_struct["report_filename"], inst_in_modules_dict)

    # запись в файл отчета иерархических путей всех instance обьектов
    project_objects_inst_report(json_struct["report_filename"], inst_in_modules_dict)


# ф-я запуска поиска иерархических путей ко всем обьектам модулей (reg, net, instance, port)
def search_allmodule_objects():
    from read_hierarchy import json_struct
    inst_in_modules_dict = get_insts_in_modules()  # словарь модулей (ключ - название модуля,
    # значение - список instance обьектов в этом модуле (с типом обьекта в круглых скобках))

    # поиск иерархических путей ко всем обьектам модулей (reg, net, instance, port)
    project_allobjects_report(json_struct["report_filename"], inst_in_modules_dict)


# ф-я разделение файлов с несколькими модулями
def splitting_modules_by_files():
    from read_hierarchy import files
    # цикл по всем файлам
    for file in files:

        filetext = get_file_text(file)  # текст файла

        # убираем теккст после endmodule (чтобы этот текст не появлялся в будущих файлах)
        filetext = re.sub(r"endmodule *: *\w+", r"endmodule", filetext)

        # список полных текстов блоков модулей файла
        moduleblocks = get_module_blocks(filetext)

        # если нашли файл с более чем 1 модулем, то разделяем файл
        if len(moduleblocks) > 1:

            # цикл обработки каждого модуля в файле
            for moduleblock in moduleblocks:

                modulename = re.search(r"module +(\w+)", moduleblock)[1]  # имя модуля

                filetext_with_cur_module = filetext  # текст файла с текущим модулем

                # цикл удаления из текста файла других модулей
                for moduleblock_another in moduleblocks:
                    if moduleblock_another == moduleblock:
                        continue
                    else:
                        filetext_with_cur_module = filetext_with_cur_module.replace(moduleblock_another, '')

                # удаялем лишние отступы
                filetext_with_cur_module = delete_indents(filetext_with_cur_module)

                # саздаем новый файл с отдельным модулем и вписываем туда основной код файла и текст модуля
                write_text_to_file(re.sub(r"[\w\.]+$", modulename, file) + ".sv",
                                                   filetext_with_cur_module)

            # удаляем файл с несколькими модулями
            os.remove(file)