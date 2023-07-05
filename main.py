import os
import deobfuscator
import ifdefprocessing
import erase_comments
import scanfiles
import obfuscator
import onlymodules

# obfuscator.launch()

# ifdefprocessing.launch()
# erase_comments.launch()
# deobfuscator.launch()

# mod = scanfiles.getallmodules(os.curdir)
# print(mod)
obfuscator.launch()
# obfuscator.obfuscate_instances(r"checkmodules.sv")
# onlymodules.launch()
print("Done!")