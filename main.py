from work_with_files import get_json_struct
import erase_comments
import ifdefprocessing
import obfuscator.deobfuscator
import read_hierarchy
import check_i
json_struct = get_json_struct(r"jsons/base.json")

if __name__ == "__main__":
    # запуск скрипта удаления комментариев
    if json_struct["tasks"]["EraseComments"]:
        erase_comments.launch()

    # запуск скрипта ifdef обработки
    if json_struct["tasks"]["IfdefPr"]:
        ifdefprocessing.launch()

    # запуск скрипта обфускации
    if json_struct["tasks"]["Obf"]:
        obfuscator.launch()

    # запуск скрипта деобфускации
    if json_struct["tasks"]["Deobf"]:
        obfuscator.deobfuscator.launch()

    # запуск скрипта чтения иерархии проекта
    if json_struct["tasks"]["ReadHierarchy"]:
        read_hierarchy.launch()

    # check_i.launch()

    print("Done!")
