import json
import check_i
import deobfuscator
import ifdefprocessing
import erase_comments
import read_hierarchy

import obfuscator

json_file = open(r"jsons/base.json", "r")
json_struct = json.load(json_file)

if json_struct["tasks"]["1"]:
    erase_comments.launch()
if json_struct["tasks"]["2"]:
    ifdefprocessing.launch()
if json_struct["tasks"]["3"]:
    obfuscator.launch()
if json_struct["tasks"]["4"]:
    deobfuscator.launch()
if json_struct["tasks"]["5"]:
    read_hierarchy.launch()
# check_i.launch()

print("Done!")