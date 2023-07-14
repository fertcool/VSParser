import json
import check_i


json_file = open(r"jsons/base.json", "r")
json_struct = json.load(json_file)
json_file.close()

import erase_comments
if json_struct["tasks"]["1"]:
    erase_comments.launch()

import ifdefprocessing
if json_struct["tasks"]["2"]:
    ifdefprocessing.launch()

import obfuscator
if json_struct["tasks"]["3"]:
    obfuscator.launch()

import deobfuscator
if json_struct["tasks"]["4"]:
    deobfuscator.launch()

import read_hierarchy
if json_struct["tasks"]["5"]:
    read_hierarchy.launch()
# check_i.launch()

print("Done!")