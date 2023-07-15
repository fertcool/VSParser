import json
import check_i


json_file = open(r"jsons/base.json", "r")
json_struct = json.load(json_file)
json_file.close()


if json_struct["tasks"]["1"]:
    import erase_comments
    erase_comments.launch()


if json_struct["tasks"]["2"]:
    import ifdefprocessing
    ifdefprocessing.launch()


if json_struct["tasks"]["3"]:
    import obfuscator
    obfuscator.launch()


if json_struct["tasks"]["4"]:
    import deobfuscator
    deobfuscator.launch()


if json_struct["tasks"]["5"]:
    import read_hierarchy
    read_hierarchy.launch()

# check_i.launch()

print("Done!")