from collections import namedtuple
import sys
import json
import datetime

import readchar
import hanzidentifier
from pinyin import pinyin as get_pinyin
from collections import namedtuple
from chin_dict.chindict import ChinDict
from hanzipy.decomposer import HanziDecomposer
from hanzipy.dictionary import HanziDictionary
from dragonmapper.transcriptions import numbered_to_accented
from tools_configs import *

rad_database = Radicals()
rad_database.load_unicode_data()
radicals = rad_database.radicals()

if rad_database.is_none():
    print("Error loading data")
    exit()

cd = ChinDict()

start_datetime = datetime.datetime.now()
now_str = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")

MAX_BUILD_ITEMS = 1000
MAX_BUILD_ITEMS = 100000

BUILD_DICT_DATA = False
CONVERT_TO_PLECO = True  #

CHAR_DICT_FILE = "char_dict.json"

print("Open char dictionary data file")
try:
    with open(CHAR_DICT_FILE, "r", encoding="utf-8") as fread:
        char_dict = json.load(fread)
except:
    print(f"No file {CHAR_DICT_FILE}")

wordset = set()

# with open("wordlists/dic_words_set.txt", "r", encoding="utf-8") as fread:
#     wordset.update(fread.read())

wordset_freq = {}

with open("wordlists/chinese_charfreq_simpl_trad.txt", "r", encoding="utf-8") as fread:
    next(fread)
    contents = fread.read()

    wordset.update(contents)

    if "\n" in wordset:
        wordset.remove("\n")

    if " " in wordset:
        wordset.remove(" ")

    wordset_freq = {word: num + 1 for num, word in enumerate(contents.split("\n"))}


def keyboard_handler(signum, frame):
    msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
    print(msg, end="", flush=True)
    res = readchar.readchar()

    if res == "y":
        print("")
        print("Saving data and quiting...")
        with open(CHAR_DICT_FILE, "w", encoding="utf-8") as fwrite:
            json.dump(char_dict, fwrite, indent=4, ensure_ascii=False)

        print(" done.")

        sys.exit(1)
    else:
        print("", end="\r", flush=True)

        print(" " * len(msg), end="", flush=True)  # clear the printed line
        print("    ", end="\r", flush=True)


print(f"{len(wordset)=}")

PATTERN_PY = r"\[(.+)\]"


def remove_non_chinese(word):
    if match_chinese := regex.findall(PATTERN_ZH, word):
        return match_chinese[0][0]  # Remove non Chinese characters
    else:
        return ""


def components_from_tree(tree, char):
    tree_matches = regex.findall(PATTERN_ZH, tree)
    if char in tree_matches:
        tree_matches.remove(char)  # Remove parent character

    return None if len(tree_matches) == 0 else tree_matches


def get_radicals(char):
    decomposition = decomposer.decompose(char, decomposition_type=2)

    radicals = decomposition["components"] if decomposition else []

    # Decomposition is same as original char => No components
    if len(radicals) == 1 and radicals[0] == char:
        radicals = []

    return radicals


searcher = HanziDictionary()
result = searcher.definition_lookup("龋", script_type="simplified")

decomposer = HanziDecomposer()
# tree = decomposer.tree("恭")
wordlist = sorted(list(wordset))

if BUILD_DICT_DATA:
    char_dict = {}

flog = open("log.txt", "w", encoding="utf-8")

LookupType = namedtuple(
    "LookupType",
    ["character", "found", "meaning", "pinyin", "components", "tree"],
    defaults=("", False, [], "", [], ""),
)


def hanzipy_lookup(char):
    found = False
    result = []
    meanings = []
    pinyin = ""

    try:
        result = searcher.definition_lookup(char, script_type="simplified")
        found = True
        for x in result:
            meanings.extend(x["definition"].split("/"))

        pinyin = numbered_to_accented(result[0]["pinyin"])  # get first pinyin
    except:
        print("No meaning")

    return found, meanings, pinyin


def is_in_char_dict(char):
    if char in char_dict and char_dict[char]["meaning"]:
        return True
    elif rad_database.is_radical_variant(char):
        norminal = rad_database.norminal(char)
        return norminal in char_dict and char_dict[norminal]["meaning"]
    else:
        return False


def lookup_symbol(char):
    if not char:
        print(f"Wrong character: {char}")
        return lookup

    found, meaning, pinyin = hanzipy_lookup(char)

    if not found:
        if rad_database.is_radical_variant(char):
            result = rad_database.lookup(char)

            return LookupType(
                char,
                found=True,
                meaning=[result["meaning"]],
                pinyin=result["pinyin"],
            )
        else:
            return lookup

    decomposition = decomposer.tree(char)

    return LookupType(
        char,
        found=True,
        meaning=meaning,
        pinyin=pinyin,
        components=decomposition["components"],
        tree=decomposition["tree"],
    )


if BUILD_DICT_DATA:
    for num, org_char in enumerate(wordlist[:MAX_BUILD_ITEMS]):
        char = remove_non_chinese(org_char)

        if not char:
            continue

        print(f"{num+1}/{len(wordlist)}: {char}")

        # org_char = "分"

        lookup = lookup_symbol(char)

        if is_in_char_dict(char):  # fmt: skip
            print(f"Already in dict: {char}")

        if not lookup.found:
            flog.write(f"{org_char}\tWrong character\n")
            print(f"Wrong character: {org_char}")

            continue

        char_dict[char] = {
            "meaning": lookup.meaning,
            "pinyin": lookup.pinyin,
            "components": lookup.components,
            "tree": lookup.tree,
        }

        if lookup.components:
            for comp_char in lookup.components:
                if is_in_char_dict(comp_char):  # fmt: skip
                    print(f"Already in dict: {comp_char}")
                    # flog.write(f"{org_char}\tAlready in dict\n")
                    continue

                comp_lookup = lookup_symbol(comp_char)

                if not comp_lookup.found:
                    flog.write(f"{comp_char}\tWrong character\n")
                    print(f"Wrong character: {org_char}")

                char_dict[comp_char] = {
                    "meaning": comp_lookup.meaning,
                    "pinyin": comp_lookup.pinyin,
                    "components": comp_lookup.components,
                    "tree": comp_lookup.tree,
                }

    print(f"{len(char_dict)=}")
    with open(CHAR_DICT_FILE, "w", encoding="utf-8") as fwrite:
        json.dump(char_dict, fwrite, indent=4, ensure_ascii=False, sort_keys=True)

flog.close()

s1 = set(char_dict.keys())
s2 = set(decomposer.characters.keys())

print(f"In char dict but not in hanzipy {len(s1-s2)=}")
print(f"In hanzipy but not in char dict {len(s2-s1)=}")


def replace_chinese_in_tree(match_obj):
    if match_obj.group(1) is not None:
        key = match_obj.group(1)
        pinyin = ""
        meaning = ""

        if rad_database.is_radical_variant(key):
            item = rad_database.lookup(key)
            pinyin = item["pinyin"]
            meaning = f"{item['meaning']} (#{item['number']})"
        elif key in char_dict:
            item = char_dict[key]
            meaning = item["meaning"][0] if item["meaning"] else "(no meaning)"
            pinyin = item["pinyin"]

        return f"{pleco_make_blue(key)} {pleco_make_italic(pinyin)} {meaning}"
        # return pleco_make_blue(match_obj.group(1))


def replace_chinese_blue(match_obj):
    if match_obj.group(1) is not None:
        key = match_obj.group(1)

        return f"{pleco_make_blue(key)}"


def replace_numbers(match_obj):
    if match_obj.group(1) is not None:
        hex_val = hex(int(match_obj.group(1)))
        return hex_val[2:].upper()
        # return pleco_make_blue(match_obj.group(1))


def find_freq(word):
    return wordset_freq[word] if word in wordset_freq else BIGNUM


def sort_by_freq(list_chars):
    items = sorted(
        [(word, find_freq(word)) for word in list_chars], key=lambda x: (x[1], x[0])
    )

    return [word for word, order in items]


if CONVERT_TO_PLECO:
    fwrite = open(f"{now_str}_char_dict_pleco.txt", "w", encoding="utf-8")
    # char_dict = json.load(fread)

    fwrite.write("// Character component dictionary\n")

    appears_chars = {}

    print(f"Before {len(char_dict)=}")
    for key in sorted(char_dict):
        if not key or key == "?" or key.isdigit():
            continue

        char = char_dict[key]
        components = char["components"]

        if rad_database.is_radical_variant(key):
            for v in rad_database.variants(key):
                if v not in char_dict:
                    char_dict[v] = char_dict[key]

        for comp in components:
            if comp.isdigit():
                continue

            if comp not in appears_chars:
                appears_chars[comp] = set([key])
            else:
                appears_chars[comp].add(key)

    print(f"After {len(char_dict)=}")

    for key in sorted(char_dict):
        char = char_dict[key]
        string = ""

        if not key or key == "?" or key.isdigit():
            continue

        pinyin = char["pinyin"]
        meanings = char["meaning"]

        # if not meanings:
        #     meanings = ["(No meaning)"]
        #     print(f"No meaning {key} {char}")

        string = f"{key}\t{pinyin}\t"
        string += f"{pleco_make_dark_gray(PC_MEANING_MARK)}\n"

        for num, meaning in enumerate(meanings):
            string += f"{number_in_cirle(num+1)} {meaning} "

        string += "\n"

        char_tree = ""
        if char["tree"]:
            string += f"{pleco_make_dark_gray(PC_TREE_MARK)}\n"
            char_tree = char["tree"]

            char_tree = regex.sub("(\d+)", replace_numbers, char_tree)
            char_tree = regex.sub(PATTERN_ZH, replace_chinese_in_tree, char_tree)

        string += f"{char_tree}"

        string += "\n"
        components = char["components"]

        if components:
            string += f"{pleco_make_dark_gray(PC_COMPONENTS_MARK)}\n"

            for comp in components:
                if comp not in char_dict:
                    flog.write(f"{comp}\tNot in char_dict\n")
                    print(f"{comp}\tNot in char_dict")
                    continue

                pinyin = char_dict[comp]["pinyin"]

                meaning_text = ""
                for num, com_meaning in enumerate(char_dict[comp]["meaning"]):
                    meaning_text += f"{number_in_cirle(num+1)} {com_meaning} "

                if rad_database.is_radical_variant(comp):
                    item = rad_database.lookup(comp)
                    variants = sorted(rad_database.variants(comp))
                    alternatives = "Alternative(s): " + PC_MIDDLE_DOT.join(variants) if rad_database.variants(comp) else ""  # fmt: skip
                    alternatives = regex.sub(
                        PATTERN_ZH, replace_chinese_blue, alternatives
                    )

                    extra_meaning = f". Radical #{item['number']}. {alternatives}"

                    meaning_text = meaning_text.strip() + extra_meaning

                    pass

                string += f"{PC_ARROW} {pleco_make_link(comp)} {pleco_make_italic(pinyin)} {meaning_text}\n"

        if key in appears_chars and (contains := sort_by_freq(appears_chars[key])):
            string += f"{pleco_make_dark_gray(PC_APPEARS_MARK)}\n"

            for contain in contains:
                string += f"{pleco_make_blue(contain)} {PC_MIDDLE_DOT} "

        string = regex.sub(PATTERN_PY, replace_num_pinyin, string)

        string = string.replace("\n", PC_NEW_LINE)
        # print(string)
        fwrite.write(f"{string}\n")

    fwrite.close()

char_dict_keys = frozenset(char_dict.keys())

print(f"In wordset but not in final list: {len(wordset - char_dict_keys)}")
print(f"Not in wordset (new components): {len(char_dict_keys - wordset)}")

end_datetime = datetime.datetime.now()

print(end_datetime - start_datetime)
