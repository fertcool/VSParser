import os
import deobfuscator
import ifdefprocessing
import erase_comments
import read_hierarchy
import scanfiles
import obfuscator


# obfuscator.launch()

# ifdefprocessing.launch()
# erase_comments.launch()
# deobfuscator.launch()

# mod = scanfiles.getallmodules(os.curdir)
# print(mod)
# obfuscator.launch()
# obfuscator.obfuscate_instances(r"checkmodules.svs")
# onlymodules.launch()


read_hierarchy.launch()

print("Done!")