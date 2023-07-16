import json

json_file = open(r"jsons/base.json", "r")
json_struct = json.load(json_file)  # словарь json
json_file.close()

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
    import deobfuscator
    deobfuscator.launch()

# запуск скрипта чтения иерархии проекта
if json_struct["tasks"]["ReadHierarchy"]:
    import read_hierarchy
    read_hierarchy.launch()

# check_i.launch()

print("Done!")