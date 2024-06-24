import os
from os.path import join

from tools_configs import DICT_DIR

dict_names = ["char_dict_pleco.txt", "radical_lookup_pleco.txt", "radical_name_pleco.txt", "tvb_pleco.txt"]

replaces = {
    chr(0xEAB1): "<br>",
    chr(0xEAB2): "<b>",
    chr(0xEAB3): "</b>",
    chr(0xEAB4): "<i>",
    chr(0xEAB5): "</i>",
    chr(0xEAB8): "",
    chr(0xEABB): "",
    "": "",
    "": "",
    "": "",
}

for filename in dict_names:
    with open(join(DICT_DIR, filename), "r", encoding="utf-8") as fread:
        name, ext = os.path.splitext(filename)
        contents = fread.read()

        for key in replaces:
            contents = contents.replace(key, replaces[key])

        lines = contents.split("\n")

        outfile = f"converted/{name}.tab"
        with open(outfile, "w", encoding="utf-8") as fwrite:
            for line in lines[1:]:
                if not line.strip():
                    continue

                items = line.split("\t")
                fwrite.write(f"{items[0]}\t{items[1]}<br>{items[2]}\n")

        print(f'{f"converted/{name}.tab"} written')
