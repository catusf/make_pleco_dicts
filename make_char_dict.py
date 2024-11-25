from collections import namedtuple
import sys
import json
import datetime
import string as string_type

import readchar
import hanzidentifier
from pinyin import get as get_pinyin
from collections import namedtuple
from chin_dict.chindict import ChinDict
from hanzipy.decomposer import HanziDecomposer
from hanzipy.dictionary import HanziDictionary
from dragonmapper.transcriptions import numbered_to_accented
from extract_hanzii_dict import MAX_ITEMS
from tools_configs import *
from os.path import join

rad_database = Radicals()
rad_database.load_radical_data()
radicals = rad_database.radicals()

if rad_database.is_none():
    print("Error loading data")
    exit()

cd = ChinDict()

start_datetime = datetime.datetime.now()
now_str = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")

MAX_APPEARANCES = 20
MAX_BUILD_ITEMS = 100000
# MAX_BUILD_ITEMS = 100

BUILD_DICT_DATA = False
CONVERT_TO_PLECO = True  #

CHAR_DICT_FILE = "char_dict.json"

print("Open char dictionary data file")
try:
    with open(join(DATA_DIR, CHAR_DICT_FILE), "r", encoding="utf-8") as fread:
        char_dict = json.load(fread)
except:
    print(f"No file {CHAR_DICT_FILE}")

char_decompositions = {}

build_ids_radical_perfect()

mnemonics_words = set()
with open(join(DATA_DIR, "mnemonics.json"), "r", encoding="utf-8") as fread:
    mnemonics = json.load(fread)
    mnemonics_words.update(mnemonics.keys())

    for key in mnemonics:
        text = "".join(mnemonics[key])

        words = set(regex.findall(PATTERN_ZH, text))
        mnemonics_words.update(words)

    # print(f"{len(mnemonics_words)=}")

with open(join(WORDLIST_DIR, "IDS_dictionary_radical_perfect.txt"), "r", encoding="utf-8") as fread:
    lines = fread.readlines()

    for line in lines:
        head, decomp = line.strip().split(":")

        char_decompositions[head] = decomp.replace(" ", "")

# with open(join(WORDLIST_DIR, "dic_words_set.txt"), "r", encoding="utf-8") as fread:
#     wordset.update(fread.read())

dict_wordset = set()
with open(join(WORDLIST_DIR, "dic_words_set.txt"), "r", encoding="utf-8") as fread:
    dict_wordset.update(fread.read())

wordset_freq = {}
charfreq_wordset = set()
wordset = set()

with open(join(WORDLIST_DIR, "chinese_charfreq_simpl_trad.txt"), "r", encoding="utf-8") as fread:
    next(fread)
    contents = fread.read()

    charfreq_wordset.update(contents)

    wordset = charfreq_wordset | dict_wordset | mnemonics_words

    # print(f"{len(charfreq_wordset)=}")
    # print(f"{len(dict_wordset)=}")
    # print(f"{len(wordset)=}")

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


# tree = decomposer.tree("恭")
wordlist = sorted(list(wordset))

if BUILD_DICT_DATA:
    char_dict = {}

    searcher = HanziDictionary()
    result = searcher.definition_lookup("龋", script_type="simplified")

    decomposer = HanziDecomposer()

    # res = decomposer.tree("寰")

flog = open("log.txt", "w", encoding="utf-8")

LookupType = namedtuple(
    "LookupType",
    ["character", "found", "meaning", "pinyin", "components", "tree"],
    defaults=("", False, [], "", [], ""),
)


def is_in_char_dict(char):
    if char in char_dict and char_dict[char]["meaning"]:
        return True
    elif rad_database.is_radical_variant(char):
        norminal = rad_database.norminal(char)
        return norminal in char_dict and char_dict[norminal]["meaning"]
    else:
        return False


def hanzipy_lookup(char):
    found = False
    results = []
    meanings = []
    pinyins = []
    # pinyin = ""

    try:
        results = searcher.definition_lookup(char, script_type="simplified")
        found = True

        # If first item is surname, move it to back
        if len(results) > 1 and results[0]["pinyin"][0].isupper():
            first = results[0]
            del results[0]
            results.append(first)

        for result in results:
            meanings.append(result["definition"].split("/"))
            pinyins.append(numbered_to_accented(result["pinyin"]))

        pinyins = list(dict.fromkeys(pinyins))
        # pinyin = "/".join(pinyins)
    except:
        print("No meaning")

    return found, meanings, pinyins


def lookup_symbol(char):
    lookup = LookupType()

    if not char:
        print(f"Wrong character: {char}")
        return lookup

    found, meanings, pinyins = hanzipy_lookup(char)

    if not found:
        if rad_database.is_radical_variant(char):
            result = rad_database.lookup(char)

            return LookupType(
                char,
                found=True,
                meaning=[[result["meaning"]]],
                pinyin=[result["pinyin"]],
            )
        else:
            return lookup

    decomposition = decomposer.tree(char)

    # Normalize components
    norminal_components = [
        rad_database.norminal(comp) if rad_database.is_radical_variant(comp) else comp
        for comp in decomposition["components"]
    ]

    return LookupType(
        char,
        found=True,
        meaning=meanings,
        pinyin=pinyins,
        components=norminal_components,
        tree=decomposition["tree"],
    )


if BUILD_DICT_DATA:
    for num, org_char in enumerate(wordlist[:MAX_BUILD_ITEMS]):
        # org_char = "打"

        char = remove_non_chinese(org_char)

        if not char:
            continue

        # print(f"{num+1}/{len(wordlist)}: {char}")

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

        results = cd.lookup_char(char)
        radical = results.radical.character
        # if radical not in lookup.components:
        #     print(f'{char} added {results.radical}')
        #     lookup.components.append(radical)

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
                    continue
                else:
                    char_dict[comp_char] = {
                        "meaning": comp_lookup.meaning,
                        "pinyin": comp_lookup.pinyin,
                        "components": comp_lookup.components,
                        "tree": comp_lookup.tree,
                    }

    # print(f"{len(char_dict)=}")
    with open(CHAR_DICT_FILE, "w", encoding="utf-8") as fwrite:
        json.dump(char_dict, fwrite, indent=4, ensure_ascii=False, sort_keys=True)


# s1 = set(char_dict.keys())
# s2 = set(decomposer.characters.keys())

# print(f"In char dict but not in hanzipy {len(s1-s2)=}")
# print(f"In hanzipy but not in char dict {len(s2-s1)=}")


def make_chinese_blue(match_obj):
    if match_obj.group(1) is not None:
        key = match_obj.group(1)

        return f"{pleco_make_blue(key)}"
        # return pleco_make_blue(match_obj.group(1))


def replace_chinese_blue(match_obj):
    if match_obj.group(1) is not None:
        key = match_obj.group(1)

        return f"{pleco_make_blue(key, MAKE_PLECO)}"


def replace_numbers(match_obj):
    if match_obj.group(1) is not None:
        hex_val = hex(int(match_obj.group(1)))
        return f"{PC_DOTTED_SQUARE} {hex_val[2:].upper()}"
        # return pleco_make_blue(match_obj.group(1))


def find_freq(word):
    return wordset_freq[word] if word in wordset_freq else BIGNUM


def sort_by_freq(list_chars):
    items = sorted([(word, find_freq(word)) for word in list_chars], key=lambda x: (x[1], x[0]))

    return [word for word, order in items]


# import pandas as pd
# import pandas as pd

# def complex_dict_to_excel(data_dict, file_path):
#     """
#     Writes a complex dictionary to an Excel file.

#     Parameters:
#     - data_dict: dict
#         The dictionary to write to the Excel file.
#         Each key will be a row with the associated fields as columns.
#     - file_path: str
#         The path where the Excel file will be saved.
#     """
#     # Prepare a list of dictionaries, each representing a row
#     rows = []

#     for character, details in data_dict.items():
#         # Flatten the details dictionary for each character
#         row = {'character': character}
#         for key, value in details.items():
#             if isinstance(value, list):
#                 new_list = []
#                 for item in value:
#                     if isinstance(item, list):
#                         new_list.extend(item)
#                     else:
#                         new_list.append(item)
#                 row[key] = ', '.join(new_list) if isinstance(new_list, list) else new_list
#                 pass
#             else:
#                 row[key] = value
#                 pass
#         rows.append(row)

#     # Convert the list of dictionaries to a DataFrame
#     df = pd.DataFrame(rows)

#     # Write the DataFrame to an Excel file
#     df.to_excel(file_path, index=False)

#     print(f"{len(data_dict)} dictionary items has been written to {file_path}")

MAKE_PLECO = False


def replace_chinese_in_tree(match_obj):
    if match_obj.group(1) is not None:
        key = match_obj.group(1)
        pinyin = ""
        meaning = ""

        viet_pron = ""
        if rad_database.is_radical_variant(key):
            item = rad_database.lookup(key)
            pinyin = item["pinyin"]
            viet_pron = f" / {item["viet-pron"]} "
            # meaning = f"{item['meaning']} (#{item['number']})"
        elif key in char_dict:
            item = char_dict[key]
            meaning = item["meaning"][0][0] if item["meaning"] else "(no meaning)"
            pinyin = item["pinyin"][0]

        return f"{pleco_make_blue(key, make_pleco=MAKE_PLECO)} {pleco_make_italic(pinyin, make_pleco=MAKE_PLECO)}{viet_pron}"


def replace_leading_spaces_with_dots(text):
    """
    Replace each space at the beginning of every line in the given text with a dot ('.').

    Args:
        text (str): The input string with multiple lines.

    Returns:
        str: The modified string with leading spaces replaced by dots.
    """
    result = []
    for line in text.splitlines():
        leading_spaces_count = len(line) - len(line.lstrip(" "))
        dots = "." * leading_spaces_count
        result.append(dots + line.lstrip(" "))
    return "\n".join(result)


def fix_for_html(text):
    """Wraps each line of text by <pre> and </pre> so that spaces will be displayed properly

    Args:
        text (_type_): _description_

    Returns:
        _type_: _description_
    """
    return "\n".join([f"<pre>{line}</pre>" for line in text.split("\n")])

import argparse

# if CONVERT_TO_PLECO:
def main():
    global MAKE_PLECO

    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Command line options for the script.")
    parser.add_argument("--make-pleco", action="store_true", help="Convert to Pleco format.")
    args = parser.parse_args()

    # Access the make-pleco argument
    MAKE_PLECO = args.make_pleco

    dict_filepath = join(DICT_DIR, f"Char-Dict_pleco.{"txt" if MAKE_PLECO else "tab"}")
    fwrite = open(dict_filepath, "w", encoding="utf-8")

    try:
        with open(join(DATA_DIR, CHAR_DICT_FILE), "r", encoding="utf-8") as fread:
            char_dict = json.load(fread)
    except:
        print(f"No file {CHAR_DICT_FILE}")
        exit()

    if MAKE_PLECO:
        fwrite.write("//Character component dictionary\n")

    appears_chars = {}

    # print(f"Before {len(char_dict)=}")

    new_wordlist = wordset  # | set(char_decompositions.keys())

    # print(f"{len(wordset)=}")
    # print(f"{len(char_decompositions)=}")
    # print(f"{len(new_wordlist)=}")
    written = 0

    for key in new_wordlist:
        if not key or key == "?" or key.isdigit() or key not in char_dict:
            continue

        char = None
        components = []
        if key in char_dict:
            char = char_dict[key]

        if key in char_decompositions:
            components = regex.findall(PATTERN_ZH, char_decompositions[key])

        # if rad_database.is_radical_variant(key):
        #     for v in rad_database.get_variants(key):
        #         if v not in char_dict:
        #             char_dict[v] = char_dict[key]

        for comp in components:
            if comp.isdigit():
                continue

            if comp not in appears_chars:
                appears_chars[comp] = set([key])
            else:
                appears_chars[comp].add(key)

    # print(f"After {len(char_dict)=}")

    char_info_dict = {}

    count = 0

    for key in new_wordlist:
        count += 1

        if count > MAX_ITEMS:
            break

        if not key or key == "?" or key.isdigit() or key not in char_dict:
            continue

        char_info = {}

        char = None
        components = []

        if key in char_dict:
            char = char_dict[key]

            pinyins = char["pinyin"]
            all_meanings = char["meaning"]

            char_info.update(char)
        else:
            pinyin_str = ""
            try:
                pinyin_str = get_pinyin(key)
            except Exception:
                pass

            pinyins = [pinyin_str]
            all_meanings = [["(No meaning)"]]

        string = ""

        decomp_str = ""

        if char and char["tree"] and key not in char_decompositions and not rad_database.is_radical_variant(key):
            char_tree_str = rad_database.norminal(char["tree"]) if len(char["tree"]) == 1 else char["tree"].replace("\n", "-")  # fmt: skip

            flog.write(f"{key}\t{'Hanzipy YES IDS No'}\t{hex(ord(key))}\t{char_tree_str}\n")  # fmt: skip

        is_rad = rad_database.norminal(key) if rad_database.is_radical_variant(key) else ""  # fmt: skip

        if char and not char["tree"] and key not in char_decompositions and not rad_database.is_radical_variant(key):  # fmt: skip
            flog.write(f"{key}\t{'Found no decompositions for'}\t{is_rad}\t{hex(ord(key))}\n")  # fmt: skip
            continue

        # Using set to avoid using regex for higher speed
        IDS_CHARS = set(["⿰", "⿱", "⿲", "⿳", "⿴", "⿵", "⿶", "⿷", "⿸", "⿹", "⿺", "⿻", " ", "&", "-", ";"])
        IDS_CHARS.update(list(string_type.digits + string_type.ascii_uppercase))
        if key in char_decompositions:
            char_info["decomposition"] = char_decompositions[key]
            components = list(dict.fromkeys([c for c in char_decompositions[key] if c not in IDS_CHARS]))
            # components1 = list(
            #     dict.fromkeys(regex.findall(PATTERN_ZH, char_decompositions[key]))
            # )  # Remove duplicates but keep order on insertion
            # assert(components1==components)
            pass
        elif rad_database.is_radical_variant(key):
            components = [key]
        else:
            components = []

        char_info["components"] = components

        if key in char_decompositions:
            decomp_str += f"{pleco_make_bold(pleco_make_dark_gray(PC_DECOMPOSITIONS_MARK, make_pleco=MAKE_PLECO), make_pleco=MAKE_PLECO)}\n"
            decomp = key + PC_WIDESPACE + char_decompositions[key].replace(" ", "")

            if MAKE_PLECO:
                decomp = regex.sub(PATTERN_ZH, make_chinese_blue, decomp)
            decomp_str += decomp
            decomp_str += "\n"
        else:
            # print(f"Found no decompositions for {key}")
            pass

        string += f"{decomp_str}"

        char_tree = ""
        if char and char["tree"] and char["tree"] != key:
            if char["tree"] == key and rad_database.is_radical_variant(key):
                char["tree"] = rad_database.norminal(key)

                pass

            string += f"{pleco_make_bold(pleco_make_dark_gray(PC_TREE_MARK, make_pleco=MAKE_PLECO), make_pleco=MAKE_PLECO)}\n"
            char_tree = char["tree"]

            char_tree = regex.sub(r"(\d+)", replace_numbers, char_tree)
            char_tree = regex.sub(PATTERN_ZH, replace_chinese_in_tree, char_tree)

            char_tree = replace_leading_spaces_with_dots(char_tree)
        char_info["tree"] = char["tree"]

        string += f"{char_tree}"

        string += "\n"

        if key in mnemonics:
            string += f"{pleco_make_bold(pleco_make_dark_gray(PC_MNEMONICS_MARK, make_pleco=MAKE_PLECO), make_pleco=MAKE_PLECO)}\n"

            mn_file, others, mn_meaning, mn_mnemonics, mn_chars = mnemonics[key]

            mn_meaning = mn_meaning.strip().capitalize()
            mn_mnemonics = mn_mnemonics.strip().capitalize()

            mn_meaning_str = f"{pleco_make_italic(mn_meaning, make_pleco=MAKE_PLECO)}" if mn_meaning else ""

            mn_mnemonics_str = f"{pleco_make_italic(mn_meaning_str, make_pleco=MAKE_PLECO)}{mn_mnemonics} {mn_chars}\n"

            if MAKE_PLECO:
                mn_mnemonics_str = regex.sub(PATTERN_ZH, replace_chinese_blue, mn_mnemonics_str)

            string += mn_mnemonics_str

            char_info["story"] = mn_mnemonics
            char_info["meaning"] = mn_meaning
            char_info["appears_in"] = mn_chars

        if components and components[0] != key:
            string += f"{pleco_make_bold(pleco_make_dark_gray(PC_COMPONENTS_MARK, make_pleco=MAKE_PLECO), make_pleco=MAKE_PLECO)}\n"

            for comp in components:
                if key == comp:
                    continue

                if comp not in char_dict and not rad_database.is_radical_variant(comp):
                    # flog.write(f"{comp}\tNot in char_dict\n")
                    # print(f"{comp}\tNot in char_dict")
                    continue

                meaning_text = ""

                comp_char = comp

                if rad_database.is_radical_variant(comp):
                    comp_char = rad_database.norminal(comp)
                    item = rad_database.lookup(comp)
                    pinyin = item["pinyin"]
                    meaning_text = f"{item["meaning"]} / {item["viet-pron"]}: {item["viet-meaning"]}" 
                    variants = sorted(rad_database.get_variants(comp))

                    if key in variants:  # If same as key headword, remove
                        variants.remove(key)

                    alternatives = "Alternatives: " + PC_MIDDLE_DOT.join(variants) if variants else ""  # fmt: skip

                    if MAKE_PLECO:
                        alternatives = regex.sub(PATTERN_ZH, replace_chinese_blue, alternatives)

                    extra_meaning = f" (#{item['number']}). {alternatives}"

                    meaning_text = meaning_text.strip() + extra_meaning
                elif comp in char_dict:
                    pinyin = char_dict[comp]["pinyin"][0]
                    meaning_text = ""
                    for num, com_meaning in enumerate(char_dict[comp]["meaning"][0]):
                        meaning_text += f"{number_in_cirle(num+1)} {com_meaning} "

                string += f"{pleco_make_link(comp_char, make_pleco=MAKE_PLECO)} {pleco_make_italic(pinyin, make_pleco=MAKE_PLECO)}: {meaning_text}\n"

        if key in appears_chars and (contains := sort_by_freq(appears_chars[key])):
            if key in contains:
                contains.remove(key)

            if contains:
                blue_chars = [pleco_make_link(char, make_pleco=MAKE_PLECO) for char in contains[:MAX_APPEARANCES]]
                appear_str = f"{pleco_make_bold(pleco_make_dark_gray(PC_APPEARS_MARK, make_pleco=MAKE_PLECO), make_pleco=MAKE_PLECO)} {len(contains)}"
                string += f"{pleco_make_dark_gray(appear_str, make_pleco=MAKE_PLECO)}\n"

                string += f"{PC_MIDDLE_DOT.join(blue_chars)}"

        string = regex.sub(PATTERN_PY, replace_num_pinyin, string)


        # Each pronunctiation and meaning need a separate line

        if MAKE_PLECO:
            for num, pinyin in enumerate(pinyins):
                meanings = all_meanings[num]

                main_string = f"{key}\t"
                
                main_string += f"{pinyin}\t"
        
                main_string += f"{pleco_make_bold(pleco_make_dark_gray(PC_MEANING_MARK, make_pleco=MAKE_PLECO), make_pleco=MAKE_PLECO)}\n"

                for num, meaning in enumerate(meanings):
                    if len(meanings) > 1:
                        main_string += f"{number_in_cirle(num+1)} {remove_chinese_with_pipe(convert_to_mark_pinyin(meaning))} "
                    else:
                        main_string += f"{remove_chinese_with_pipe(convert_to_mark_pinyin(meaning))} "

                main_string = main_string.strip()
                main_string += "\n"

            main_string += string

            main_string = pleco_make_new_line(main_string, make_pleco=MAKE_PLECO)
            # print(string)
            fwrite.write(f"{main_string}\n")
            written += 1
        else:
            main_string = f"{key}\t"
                
            for num, pinyin in enumerate(pinyins):
                meanings = all_meanings[num]

                main_string += f"[{pinyin}]\n"
        
                for num, meaning in enumerate(meanings):
                    if len(meanings) > 1:
                        main_string += f"{number_in_cirle(num+1)} {remove_chinese_with_pipe(convert_to_mark_pinyin(meaning))} "
                    else:
                        main_string += f"{remove_chinese_with_pipe(convert_to_mark_pinyin(meaning))} "

                main_string = main_string.strip()
                main_string += "\n"

            main_string += string

            main_string = pleco_make_new_line(main_string, make_pleco=MAKE_PLECO)
            # print(string)
            fwrite.write(f"{main_string}\n")
            written += 1

        char_info["my_story"] = ""
        char_info["picture"] = ""
        char_info["frequency_rank"] = wordset_freq[key] if key in wordset_freq else 10000000

        # Only care about simplfied chars now
        if hanzidentifier.is_simplified(key):
            char_info_dict[key] = char_info

        pass

    fwrite.close()

    print(f"{written=}")
    print(f"Dictionary written {dict_filepath}")
    
if __name__ == "__main__":
    main()


    # complex_dict_to_excel(char_info_dict, "char_dict.xlsx")

    # char_dict_keys = frozenset(char_dict.keys())


    # print(f"In wordset but not in final list: {len(wordset - char_dict_keys)}")
    # print(f"Not in wordset (new components): {len(char_dict_keys - wordset)}")

    end_datetime = datetime.datetime.now()

    print(f"Elapsed time: {end_datetime - start_datetime}")
    flog.close()

