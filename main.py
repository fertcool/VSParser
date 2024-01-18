from work_with_files import get_json_struct

json_struct = get_json_struct(r"jsons/base.json")

if __name__ == "__main__":
    # запуск скрипта удаления комментариев
    if json_struct["tasks"]["EraseComments"]:
        import erase_comments
        erase_comments.launch()

    # запуск скрипта ifdef обработки
    if json_struct["tasks"]["IfdefPr"]:
        import ifdefprocessing
        ifdefprocessing.launch()

    # запуск скрипта обфускации
    if json_struct["tasks"]["Obf"]:
        import obfuscator
        obfuscator.launch()

    # запуск скрипта деобфускации
    if json_struct["tasks"]["Deobf"]:
        import obfuscator.deobfuscator
        obfuscator.deobfuscator.launch()

    # запуск скрипта чтения иерархии проекта
    if json_struct["tasks"]["ReadHierarchy"]:
        import read_hierarchy
        read_hierarchy.launch()

    # check_i.launch()

    print("Done!")
