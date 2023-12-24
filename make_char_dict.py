import sys
import json
import datetime

import readchar
import hanzidentifier
from pinyin import pinyin as get_pinyin

from chin_dict.chindict import ChinDict
import regex as re
from dragonmapper.transcriptions import numbered_to_accented
from tools_configs import (
    number_in_cirle,
    pleco_make_blue,
    pleco_make_dark_gray,
    pleco_make_italic,
    pleco_make_link,
)

cd = ChinDict()


start_datetime = datetime.datetime.now()
now_str = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")

MAX_BUILD_ITEMS = 100000
MAX_BUILD_ITEMS = 100

BUILD_DICT_DATA = False
CONVERT_TO_PLECO = True  #


PC_NEW_LINE = chr(0xEAB1)
PC_HANVIET_MARK = "HÁN VIỆT"
PC_RELATED_MARK = "LIÊN QUAN"
PC_VIDU_OLD_MARK = "Ví dụ:"
PC_VIDU_NEW_MARK = "VÍ DỤ"
PC_DIAMOND = "❖"
PC_ARROW = "»"
PC_TRIANGLE = "▶"  # ►
PC_DIAMOND_SUIT = "♦"
PC_HEART_SUIT = "♥"
PC_CLUB_SUIT = "♣"
PC_MIDDLE_DOT = "·"

PC_SPADE_SUIT = "♠"

PC_MEANING_MARK = "MEANING"
PC_TREE_MARK = "TREE"
PC_COMPONENTS_MARK = "COMPONENTS"
PC_CONTAINS_MARK = "CONTAINS"

CHAR_DICT_FILE = "char_dict.json"

# char_dict = {}

print("Open char dictionary data file")
try:
    with open(CHAR_DICT_FILE, "r", encoding="utf-8") as fread:
        char_dict = json.load(fread)
except:
    print(f"No file {CHAR_DICT_FILE}")

wordset = set()

with open("dic_words_set.txt", "r", encoding="utf-8") as fread:
    wordset.update(fread.read())

radical_set = {}
with open("./wordlists/radicals.txt", "r", encoding="utf-8") as fread:
    next(fread)

    for line in fread:
        char_radical, meaning, number, alternatives = line.split("\t")

        radical_set[char_radical] = {
            "meaning": meaning,
            "number": number,
            "alternatives": alternatives.strip(),
        }


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

PATTERN_ZH = (
    r"([\p{Block=CJK_Unified_Ideographs}\p{Block=CJK_Compatibility}\p{Block=CJK_Compatibility_Forms}"
    r"\p{Block=CJK_Compatibility_Ideographs}\p{Block=CJK_Compatibility_Ideographs_Supplement}"
    r"\p{Block=CJK_Radicals_Supplement}\p{Block=CJK_Strokes}\p{Block=CJK_Symbols_And_Punctuation}"
    r"\p{Block=CJK_Unified_Ideographs}\p{Block=CJK_Unified_Ideographs_Extension_A}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_B}\p{Block=CJK_Unified_Ideographs_Extension_C}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_D}\p{Block=CJK_Unified_Ideographs_Extension_E}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_F}\p{Block=Enclosed_CJK_Letters_And_Months}])"
)

PATTERN_PY = r"\[(.+)\]"

wordlist = sorted(list(wordset))


def remove_non_chinese(word):
    if match_chinese := re.findall(PATTERN_ZH, word):
        return match_chinese[0][0]  # Remove non Chinese characters
    else:
        return ""


def components_from_tree(tree, char):
    tree_matches = re.findall(PATTERN_ZH, tree)
    if char in tree_matches:
        tree_matches.remove(char)  # Remove parent character

    return None if len(tree_matches) == 0 else tree_matches


# char_dict = {}

if BUILD_DICT_DATA:
    for num, org_char in enumerate(wordlist[:MAX_BUILD_ITEMS]):
        # org_char = '海'
        char = remove_non_chinese(org_char)

        if not char:
            print(f"Wrong character: {org_char}")

        if not hanzidentifier.is_simplified(char):
            continue

        # if char in char_dict:
        #     continue

        string = ""
        component_set = {}

        char_result = cd.lookup_char(char)
        char_tree = char_result.tree(show=False).strip()
        char_meaning = char_result.meaning

        if char in char_dict and (
            char_dict[char]["meaning"] and char_dict[char]["components"]
        ):
            print(f"Already in dict: {char}")

            continue

        print(f"{num+1}/{len(wordlist)}: {char}")

        char_pinyin = get_pinyin.get(char)

        if char_tree == char:
            char_tree = ""

        tree_components = components_from_tree(char_tree, char)

        char_radical = (
            char_result.radical.character if hasattr(char_result, "radical") else ""
        )

        if not char_meaning:
            print(f"Wrong character: {org_char}")
            continue

        char_dict[char] = {
            "meaning": char_meaning,
            "pinyin": char_pinyin,
            "components": tree_components,
            "tree": char_tree,
            "radical": char_radical,
        }

        if tree_components:
            for comp_char in tree_components:
                comp_result = cd.lookup_char(comp_char)
                comp_tree = comp_result.tree(show=False).strip()

                if comp_char in char_dict and (
                    char_dict[comp_char]["meaning"]
                    and char_dict[comp_char]["components"]
                ):
                    print(f"Already in dict: {comp_char}")
                    continue

                if comp_tree == comp_char:
                    comp_tree = ""

                comp_tree_components = components_from_tree(comp_tree, comp_char)

                pinyin = get_pinyin.get(comp_char)
                comp_radical = (
                    comp_result.radical.character
                    if hasattr(comp_result, "radical")
                    else ""
                )

                char_dict[comp_char] = {
                    "meaning": comp_result.meaning,
                    "pinyin": pinyin,
                    "tree": comp_tree,
                    "radical": comp_radical,
                    "components": comp_tree_components,
                }

    # a = re.search(r"([一-龥]+)(\[.+\])", '/'.join(char_result.meaning))
    # Sort items in order of appearance in the tree
    # items = sorted(component_set.items(), key=lambda x: x[1]['order'])
    # component_list = []

    # for item in items:
    #     com_char = item[0]

    #     char_dict[com_char] = item[1]['dict']
    #     component_list.append(com_char)

    # print(string)
    # string = string.replace('\n', PC_NEW_LINE)
    # fwrite.write(f'{string}\n')

    print(f"{len(char_dict)=}")
    with open(CHAR_DICT_FILE, "w", encoding="utf-8") as fwrite:
        json.dump(char_dict, fwrite, indent=4, ensure_ascii=False, sort_keys=True)


def replace_blue(match_obj):
    if match_obj.group(1) is not None:
        return pleco_make_blue(match_obj.group(1))


def replace_num_pinyin(match_obj):
    if match_obj.group(1) is not None:
        return pleco_make_italic(numbered_to_accented(match_obj.group(1)))


if CONVERT_TO_PLECO:
    fwrite = open(f"{now_str}_char_dict_pleco.txt", "w", encoding="utf-8")
    # char_dict = json.load(fread)

    fwrite.write("// Character component dictionary\n")

    containing_chars = {}

    for key in sorted(char_dict):
        char = char_dict[key]
        components = char["components"]

        if components:
            for comp in components:
                if comp not in containing_chars:
                    containing_chars[comp] = set([key])
                else:
                    containing_chars[comp].add(key)

    for key in sorted(char_dict):
        char = char_dict[key]
        string = ""

        string = f"{key}\t{char['pinyin']}\t"
        meanings = char["meaning"]

        if key in radical_set:
            item = radical_set[key]

            if meanings:
                for num, text in enumerate(meanings):
                    at = text.find("radical in")
                    if at >= 0:
                        del meanings[num]
                        break

            if not meanings:
                meanings = []

            alternatives = (
                " Alternative(s): " + item["alternatives"]
                if item["alternatives"]
                else ""
            )

            meanings.insert(
                0, f"{item['meaning']} (radical number {item['number']}){alternatives}"
            )

        if not meanings:
            meanings = ["(No meaning)"]

        string += f"{pleco_make_dark_gray(PC_MEANING_MARK)}\n"

        for num, meaning in enumerate(meanings):
            string += f"{number_in_cirle(num+1)} {meaning} "

        string += "\n"

        if "tree" in char and char["tree"]:
            string += f"{pleco_make_dark_gray(PC_TREE_MARK)}\n"
            char_tree = char["tree"]
            char_tree = re.sub(PATTERN_ZH, replace_blue, char_tree)

            string += f"{char_tree}"

        string += "\n"
        components = char["components"]

        if components:
            string += f"{pleco_make_dark_gray(PC_COMPONENTS_MARK)}\n"

            for comp in components:
                # comp_meaning = ' / '.join(
                #     char_dict[comp]['meaning'] if char_dict[comp]['meaning'] else ['(No meaning)'])
                meaning_text = ""

                pinyin = get_pinyin.get(comp)
                if comp not in char_dict or not char_dict[comp]["meaning"]:
                    meaning_text = "(No meaning)"
                else:
                    for num, com_meaning in enumerate(char_dict[comp]["meaning"]):
                        meaning_text += f"{number_in_cirle(num+1)} {com_meaning} "

                string += f"{PC_ARROW} {pleco_make_link(comp)} {pleco_make_italic(pinyin)} {meaning_text}\n"

        if key in containing_chars and (contains := containing_chars[key]):
            string += f"{pleco_make_dark_gray(PC_CONTAINS_MARK)}\n"

            for contain in contains:
                string += f"{pleco_make_blue(contain)} {PC_MIDDLE_DOT} "

        string = re.sub(PATTERN_PY, replace_num_pinyin, string)

        string = string.replace("\n", PC_NEW_LINE)
        # print(string)
        fwrite.write(f"{string}\n")

    fwrite.close()

end_datetime = datetime.datetime.now()

print(end_datetime - start_datetime)
