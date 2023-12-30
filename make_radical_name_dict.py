import sys
import json
import datetime

# import readchar
import hanzidentifier
from pinyin import get as get_pinyin

from chin_dict.chindict import ChinDict
import regex as re
from dragonmapper.transcriptions import numbered_to_accented
from zmq import has
from tools_configs import (
    replace_blue,
    pleco_make_blue,
    pleco_make_dark_gray,
    pleco_make_italic,
    pleco_make_link,
    pleco_make_bold,
    number_in_cirle,
    replace_blue,
    PC_NEW_LINE,
    PC_MIDDLE_DOT,
    PATTERN_ZH,
    PC_TRIANGLE,
    Radicals,
)

VERSION = "0.9"

HOME_PAGE = "偏旁"
NAME_PAGE = "有名字"

fwrite = open(f"radical_name_pleco.txt", "w", encoding="utf-8")
fwrite.write(f"// Radical name dictionary (v{VERSION})\n")

FIX_SPECIAL_PINYIN = {"sānpiēér": "sānpiěr"}

rad_database = Radicals()
rad_database.load_unicode_data()
radicals = rad_database.radicals()

if rad_database.is_none():
    print("Error loading data")
    exit()

# Prepapare data for paginating radicals by number of strokes
radicals_by_strokes = {}
for rad in radicals:
    data = rad_database.lookup(rad)
    strokes = data["strokes"]

    if strokes not in radicals_by_strokes:
        radicals_by_strokes[strokes] = [rad]
    else:
        radicals_by_strokes[strokes].append(rad)

for strokes in radicals_by_strokes:
    radicals_by_strokes[strokes].sort()

radical_strok_items = list(radicals_by_strokes.items())
radical_strok_items.sort(key=lambda x: x[0])

stroke_levels = [x[0] for x in radical_strok_items]

string = ""

string = f"{HOME_PAGE}\tpiānpáng\t{pleco_make_dark_gray('RADICALS HOMEPAGE')}\n"


for level in stroke_levels:
    string += f"{number_in_cirle(level)}\n"
    items = [pleco_make_link(radical) for radical in radicals_by_strokes[level]]

    string += f" {PC_MIDDLE_DOT} ".join(items)

    string += "\n"

string += f"{pleco_make_dark_gray('WITH NAMES')} {pleco_make_link(NAME_PAGE)}\n"

items = [pleco_make_link(rad) for rad in radicals if rad_database.lookup(rad)["name"] ]  # fmt: skip

string += f" {PC_MIDDLE_DOT} ".join(items)
string = string.replace("\n", PC_NEW_LINE)
fwrite.write(f"{string}\n")

# Write item for radicals with names
string_has_name = (
    f"{NAME_PAGE}\tyǒu míngzì\t{pleco_make_dark_gray('RADICALS WITH NAMES')}\n"
)

for rad in radicals:
    # fmt: off
    variants = rad_database.variants(rad)
    data = rad_database.lookup(rad)
    meaning = data["meaning"]
    pinyin = data["pinyin"]
    items = data["examples"].split("、")
    examples = PC_MIDDLE_DOT.join([pleco_make_blue(item) for item in items])
    name = data["name"]
    name_pinyin = get_pinyin(name)
    if name_pinyin in FIX_SPECIAL_PINYIN:
        name_pinyin = FIX_SPECIAL_PINYIN[name_pinyin]

    number = data["number"]
    notes = data["useful"]["notes"] if data["useful"] else ""
    items = data["useful"]["distinguish"] if data["useful"] else []
    distinguish = PC_MIDDLE_DOT.join([pleco_make_blue(item) for item in items])
    
    variants_usefule = data["useful"]["variants"] if data["useful"] else ""
    rank = data["useful"]["rank"] if data["useful"] else ""
    mnemonic = data["useful"]["mnemonic"] if data["useful"] else ""
    examples_str = f"\n{pleco_make_dark_gray('EXAMPLES')} {examples}"
    back_home = f"\n\n{pleco_make_dark_gray('HOMEPAGE')} {PC_TRIANGLE} {pleco_make_link(HOME_PAGE)}"

    for var in variants:
        string = f"{var}\t{pinyin}\tVariant of radical {pleco_make_link(rad)} ({pleco_make_bold(meaning)}){examples_str}{back_home}"
        print(string)
        string = string.replace("\n", PC_NEW_LINE)

        fwrite.write(f"{string}\n")

    number_str = f"Kangxi radical number {number}"
    variants_str = f"\n{pleco_make_dark_gray('VARIANTS')} {PC_MIDDLE_DOT.join([pleco_make_blue(item) for item in variants])}" if variants else ""
    name_str = f"\n{pleco_make_dark_gray('NAME')} {pleco_make_blue(name)} {name_pinyin}" if name else ""
    meaning_str = f"\n{pleco_make_dark_gray('MEANING')} {pleco_make_bold(meaning)}"
    mnemonic_str = f"\n{pleco_make_dark_gray('MNEMONIC')} {pleco_make_italic(mnemonic)}" if mnemonic else ""
    notes_str = f"\n{pleco_make_dark_gray('NOTES')} {pleco_make_italic(notes)}" if notes else ""
    distinguish_str = f"\n{pleco_make_dark_gray('DISTINGHUISH FROM')} {distinguish}" if distinguish else ""
    rank_str = f"\n{pleco_make_dark_gray('RANK')} {rank}" if rank else ""

    if name:
        string_has_name += f"{pleco_make_link(rad)} {name_pinyin} {pleco_make_blue(name)} {pleco_make_bold(meaning)}\n"
    
        string_name_head = f"{name}\t{name_pinyin}\tName of radical {pleco_make_link(rad)}{meaning_str}{examples_str}{back_home}"
        string_name_head = string_name_head.replace("\n", PC_NEW_LINE)
        fwrite.write(f"{string_name_head}\n")

    string = f"{rad}\t{pinyin}\t{number_str}{name_str}{variants_str}{meaning_str}{examples_str}{mnemonic_str}{rank_str}{distinguish_str}{notes_str}{back_home}"
    string = string.replace("\n", PC_NEW_LINE)
    # print(string)
    fwrite.write(f"{string}\n")
    # fmt: on

string_has_name += back_home
string_has_name = string_has_name.replace("\n", PC_NEW_LINE)
fwrite.write(f"{string_has_name}\n")

fwrite.close()
exit()
