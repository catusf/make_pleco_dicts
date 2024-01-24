import hanzidentifier
import os
import regex
import urllib.parse
import json

from dragonmapper.transcriptions import numbered_to_accented

TOP_WORDS_50k = "top_50k_words.txt"
TOP_WORDS_24K = "top_words_24k.txt"
TOP_WORDS_1M = "top_1m_words.txt"
BIGNUM = 20000000

PATTERN_URL = r"(https://hanzii.net/search/word/(.+?)\?hl=vi)"
PATTERN_ZH = r"[一-龥]+"
PATTERN_REDUNDANT = r"[.!?。！？]"

HTML_FOLDER = "html"
WORDLIST_FOLDER = "wordlists"

WAIT_TIME = 7  # Seconds

MARKER_GOOD_FILE = "Chi tiết từ"
MARKER_HAS_DEF_FILE = "Đóng góp bản dịch"

PC_NEW_LINE = chr(0xEAB1)
PC_HANVIET_MARK = "HÁN VIỆT"
PC_RELATED_MARK = "LIÊN QUAN"
PC_VIDU_OLD_MARK = "Ví dụ:"
PC_VIDU_NEW_MARK = "VÍ DỤ"
PC_DIAMOND = "❖"
PC_ARROW = "»"
PC_TRIANGLE = "►"  # ▶
PC_RIGHT_TRIANGLE = "▸"  # ▸
PC_LEFT_TRIANGLE = "◂"
PC_DIAMOND_SUIT = "♦"
PC_HEART_SUIT = "♥"
PC_CLUB_SUIT = "♣"
PC_SPADE_SUIT = "♠"
PC_MIDDLE_DOT = "·"
PC_WIDESPACE = "\u3000"
PC_DOTTED_SQUARE = "\u2B1A"

PC_MEANING_MARK = "MEANING"
PC_TREE_MARK = "TREE"
PC_DECOMPOSITIONS_MARK = "DECOMPOSITIONS"
PC_MNEMONICS_MARK = "MNEMONICS"
PC_COMPONENTS_MARK = "COMPONENTS"
PC_APPEARS_MARK = "APPEARS IN"

PATTERN_ZH = (
    r"([\p{Block=CJK_Unified_Ideographs}\p{Block=CJK_Compatibility}\p{Block=CJK_Compatibility_Forms}"
    r"\p{Block=CJK_Compatibility_Ideographs}\p{Block=CJK_Compatibility_Ideographs_Supplement}"
    r"\p{Block=Kangxi_Radicals}\p{Block=CJK_Radicals_Supplement}\p{Block=CJK_Strokes}\p{Block=CJK_Symbols_And_Punctuation}"
    r"\p{Block=CJK_Unified_Ideographs}\p{Block=CJK_Unified_Ideographs_Extension_A}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_B}\p{Block=CJK_Unified_Ideographs_Extension_C}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_D}\p{Block=CJK_Unified_Ideographs_Extension_E}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_F}\p{Block=Enclosed_CJK_Letters_And_Months}])"
)

PATTERN_ZH_MUL = (
    r"([\p{Block=CJK_Unified_Ideographs}\p{Block=CJK_Compatibility}\p{Block=CJK_Compatibility_Forms}"
    r"\p{Block=CJK_Compatibility_Ideographs}\p{Block=CJK_Compatibility_Ideographs_Supplement}"
    r"\p{Block=Kangxi_Radicals}\p{Block=CJK_Radicals_Supplement}\p{Block=CJK_Strokes}\p{Block=CJK_Symbols_And_Punctuation}"
    r"\p{Block=CJK_Unified_Ideographs}\p{Block=CJK_Unified_Ideographs_Extension_A}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_B}\p{Block=CJK_Unified_Ideographs_Extension_C}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_D}\p{Block=CJK_Unified_Ideographs_Extension_E}"
    r"\p{Block=CJK_Unified_Ideographs_Extension_F}\p{Block=Enclosed_CJK_Letters_And_Months}]+)"
)


def find_freq(word):
    return wordset_freq[word] if word in wordset_freq else BIGNUM


def sort_by_freq(list_chars):
    items = sorted([(word, find_freq(word)) for word in list_chars], key=lambda x: (x[1], x[0]))

    return [word for word, order in items]


def headword_to_url(word):
    quoted = urllib.parse.quote(word, encoding="utf-8", errors="replace")
    return f"https://hanzii.net/search/word/{quoted}?hl=vi"


def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


def pure_traditional(word):
    return hanzidentifier.is_traditional(word) and not hanzidentifier.is_simplified(word)


def get_chinese_words(text):
    headwords = regex.findall(PATTERN_ZH, text, flags=regex.DOTALL)

    return [word for word in headwords if hanzidentifier.is_simplified(word)]


def url_to_headword(url):
    match = regex.search(PATTERN_URL, url)

    if not match:
        return None

    headword = match.group(2)
    return urllib.parse.unquote(headword, encoding="utf-8", errors="replace")


def convert_to_num(match):
    """
    The function `convert_to_num` is for convert character to hex value in a string for debug reasons.

    Usafe: re.sub(NEED_CONVERT, convert_to_num, text)

    :param match: The `match` parameter is a regular expression match object. It represents the matched
    substring and provides access to various properties and methods for working with the match. In this
    case, the `match` object is expected to have a group 1, which represents the matched character
    :return: The function `convert_to_num` returns a string that represents the hexadecimal value of the
    character passed as an argument, enclosed in vertical bars.
    """
    t = match.group(1)
    n = hex(ord(t)).replace("0x", "")
    return f"|{n}|"


def number_in_cirle(number):
    """
    Gets the Unicode character coresponding to a number
    """
    if number < 0 or number > 20:
        # print(f"Number {number} too big for number-in-circle. Use original")
        return f"({number})"
        # raise ValueError
    else:
        return chr(9311 + number)


def remove_redundant_characters(text):
    return regex.sub(PATTERN_REDUNDANT, "", text).replace("''", "'")


def remove_chinese_bracket(text):
    return regex.sub("【(.+?)】", r"\1", text)


def remove_traditional_text(text):
    return regex.sub("【.+?】", "", text)


def remove_see_more_examples(text):
    return regex.sub(r"Xem thêm \d+ ví dụ nữa", "", text)


def pleco_make_bold(text):
    return f"{chr(0xEAB2)}{text}{chr(0xEAB3)}"


def pleco_make_blue(text):
    # return f"{text}"  # Deep Sky Blue
    return f"{text}"  # Dodge Blue


def pleco_make_gray(text):  # Light Slate Gray
    return f"{text}"


def pleco_make_dark_gray(text):  # Light Slate Gray
    return f"{text}"


def pleco_make_light_gray(text):  # Light Slate Gray
    return f"{text}"


def pleco_make_italic(text):
    return f"{chr(0xEAB4)}{text}{chr(0xEAB5)}"


def pleco_make_link(text):
    return f"{chr(0xEAB8)}{text}{chr(0xEABB)}"


def load_frequent_words(filename):
    with open(f"{WORDLIST_FOLDER}/{filename}", "r", encoding="utf-8") as fin:
        # Remove first line with comments
        lines = [line.strip() for line in fin.readlines()][1:]

    return lines


def make_list(list_items):
    if not list_items:
        return []
    else:
        return list_items


def replace_blue(match_obj):
    if match_obj.group(1) is not None:
        return pleco_make_blue(match_obj.group(1))


def replace_num_pinyin(match_obj):
    if match_obj.group(1) is not None:
        return pleco_make_italic(numbered_to_accented(match_obj.group(1)))


import json
import re


class Radicals:
    def __init__(self):
        self.set_none()

    def is_none(self):
        return not (self.radical_set and self.radical_list and self.radical_nominals)

    def set_none(self):
        self.radical_set = {}
        self.radical_list = []
        self.radical_nominals = {}
        # self.radical_variants = {}

        self.radical_set_file = "./wordlists/radical_set.json"
        self.radical_norminal_file = "./wordlists/radical_radical_norminals.json"
        self.radical_info_file = "./wordlists/radicals.txt"
        self.radicals_useful_info_file = "./wordlists/radicals-useful_info.txt"
        self.kangxi_radical_file = "./wordlists/kangxi_radical_unicode.txt"
        self.kangxi_radical_supplement_file = "./wordlists/kangxi_radical_supplement_unicode.txt"  # fmt: skip

    # Gets the radicals
    def radicals(self):
        return self.radical_list

    # Gets all variants of the radicals
    def variants(self):
        return self.radical_nominals.keys()

    def is_radical_variant(self, radical):
        return radical in self.radical_nominals

    def is_standalone(self, radical):
        if not self.is_radical_variant(radical):
            return False

        return self.radical_set[self.norminal(radical)]["standalone"] == radical

    # Get variant forms of a radical/variant
    def get_variants(self, radical):
        return self.radical_set[self.norminal(radical)]["variants"]

    def _setup_norminals(self):
        for symbol in self.radical_set:
            self.radical_nominals[symbol] = symbol
            variants = self.radical_set[symbol]["variants"]

            for variant in variants:
                self.radical_nominals[variant] = symbol

    def norminal(self, variant):
        return self.radical_nominals[variant]

    def lookup(self, radical):
        return self.radical_set[self.norminal(radical)]

    def load_radical_data(self):
        # with open(radical_norminal_file, "r", encoding="utf-8") as file:
        #     self.radical_nominals = json.load(file)

        self.set_none()

        # exceptions = {"⼋": ["丷"]}

        with open(self.radical_set_file, "r", encoding="utf-8") as file:
            self.radical_set = json.load(file)

            self.radical_list = sorted(list(self.radical_set))

            for symbol in self.radical_set:
                self.radical_nominals[symbol] = symbol
                variants = self.radical_set[symbol]["variants"]

                # if symbol in exceptions:
                #     variants.extend(exceptions[symbol])

                for variant in variants:
                    self.radical_nominals[variant] = symbol

    def save_radical_data(self):
        # with open(self.radical_norminal_file, "w", encoding="utf-8") as file:
        #     json.dump(self.radical_nominals, file, indent=4, ensure_ascii=False)
        for rad in self.radical_set:
            self.radical_set[rad]["variants"] = sorted(self.radical_set[rad]["variants"])
            self.radical_set[rad]["codepoint"] = hex(ord(rad))
            self.radical_set[rad]["standalone_codepoint"] = (
                hex(ord(self.radical_set[rad]["standalone"])) if self.radical_set[rad]["standalone"] else ""
            )

            self.radical_set[rad]["variant_codepoint"] = [hex(ord(item)) for item in self.radical_set[rad]["variants"]]

        with open(self.radical_set_file, "w", encoding="utf-8") as file:
            json.dump(self.radical_set, file, indent=4, ensure_ascii=False)

    def __load_unicode_data__(self):
        """
        Loads raw data from Unicode dataand other files, then saves to processed data
        """
        self.set_none()

        try:
            kangxi_unicode_set = {}
            kangxi_suppl_unicode_set = {}

            with open(self.kangxi_radical_file, "r", encoding="utf-8") as fread:
                next(fread)
                kangxi_unicode_set = {}

                for line in fread:
                    # print(line)
                    radical_strok_items = line.strip().split("\t")
                    codepoint, symbol, name, rad_number = radical_strok_items[:4]
                    symbol = symbol.strip()
                    number = int(regex.search(r"(\d+)", rad_number).group(1))

                    if len(radical_strok_items) > 4:
                        app_ex, app_code, app_sym = radical_strok_items[4].split(" ")
                        kangxi_unicode_set[number] = {
                            "symbol": (symbol, codepoint),
                            "name": name.strip(),
                            "number": number,
                            "approx_symbol": set([(app_sym, app_code)]),
                        }

                    if len(radical_strok_items) > 5:
                        app_ex1, app_code1, app_sym1 = radical_strok_items[5].split(" ")
                        kangxi_unicode_set[number]["approx_symbol"].add((app_code1, app_sym1))

            with open(self.kangxi_radical_supplement_file, "r", encoding="utf-8") as fread:
                next(fread)
                kangxi_suppl_unicode_set = {}

                for line in fread:
                    # print(line)
                    radical_strok_items = line.strip().split("\t")
                    codepoint, symbol, name, rad_number = radical_strok_items[:4]
                    symbol = symbol.strip()
                    number = (
                        int(match.group(1)) if (match := regex.search(r"Kangxi Radical (\d+)", rad_number)) else None
                    )

                    if not number:
                        print(f"Wrong line {line}")
                        continue

                    if number not in kangxi_suppl_unicode_set:
                        kangxi_suppl_unicode_set[number] = set([(symbol, codepoint)])
                    else:
                        kangxi_suppl_unicode_set[number].add((symbol, codepoint))

                    index = 4
                    if len(radical_strok_items) > index:
                        if radical_strok_items[index].find("form") >= 0:
                            index += 1

                        # print(items[index])
                        app_ex, app_code, app_sym = radical_strok_items[index].split(" ")
                        kangxi_suppl_unicode_set[number].add((app_sym, app_code))

                        index += 1
                    if len(radical_strok_items) > index:
                        app_ex1, app_code1, app_sym1 = radical_strok_items[index].split(" ")
                        kangxi_suppl_unicode_set[number].add((app_sym1, app_code1))
                        index += 1

            for number in kangxi_suppl_unicode_set:
                kangxi_unicode_set[number]["approx_symbol"].update(kangxi_suppl_unicode_set[number])

            for number in kangxi_unicode_set:
                symbol, codepoint = kangxi_unicode_set[number]["symbol"]
                self.radical_nominals[symbol] = symbol
                variants = kangxi_unicode_set[number]["approx_symbol"]

                for variant, var_codepoint in variants:
                    self.radical_nominals[variant] = symbol

            usefull_radical_info = {}
            # fmt: off
            with open(self.radicals_useful_info_file, "r", encoding="utf-8") as fread:
                for line in fread.readlines():
                    rad, pinyin, define = line.strip().split("\t")

                    notes = match.group(1) if (match := regex.search(r"Notes:(.+?)", define)) else ""
                    distinguish = match.group(1).split(" ") if (match := regex.search(r"Distinguish From: (.+)", define)) else [] 
                    variants = list(match.group(1)) if (match := regex.search(r"Variants:(.+?)", define)) else []
                    rank = match.group(1) if (match := regex.search(r"RANK: (.+?)", define)) else ""
                    mnemonic = match.group(1) if (match := regex.search(r"Mnemonic:(.+?)", define)) else ""

                    usefull_radical_info[rad] = {
                        "distinguish": distinguish,
                        "variants": variants,
                        "rank": rank,
                        "mnemonic": mnemonic,
                        "notes": notes,
                    }
                    # print(
                    #     f"{rad} Notes {notes}\n{distinguish=}\t{variants=}\t{rank=}\t{mnemonic=}"
                    # )
                    pass

            self.radical_set = {}
            # old_radical_set = {}
            with open(self.radical_info_file, "r", encoding="utf-8") as fread:
                next(fread)

                for line in fread:
                    (
                        number,
                        char_radical,
                        strokes,
                        meaning,
                        name,
                        pinyin,
                        vietnamese,
                        frequency,
                        simplified,
                        examples,
                    ) = line.strip().split("\t")

                    # items = alternatives.split("/")
                    rad = char_radical[0]
                    self.radical_set[self.radical_nominals[rad]] = {
                        "meaning": meaning,
                        "number": int(number),
                        "pinyin": pinyin,
                        "name": name.strip(),
                        "strokes": int(strokes),
                        "frequency": frequency,
                        "examples": examples,
                        "useful": {},
                    }

                    if rad in usefull_radical_info:
                        self.radical_set[self.radical_nominals[rad]][
                            "useful"
                        ] = usefull_radical_info[rad]

            for number in kangxi_unicode_set:
                symbol, codepoint = kangxi_unicode_set[number]["symbol"]
                variants = kangxi_unicode_set[number]["approx_symbol"]
                self.radical_set[symbol]["variants"] = []

                for variant, var_codepoint in variants:
                    self.radical_set[symbol]["variants"].append(variant)

            # self.save_radical_data()

            self.load_radical_data()

            return True

        except IOError as e:
            print(e)
            return False


# fmt: on

import regex


def build_ids_radical_perfect():
    char_decompositions = {}

    full_char_decompositions = {}
    radical_found = set()
    radical_norminal_found = set()

    rad_db = Radicals()
    rad_db.load_radical_data()

    non_rad_components = {}

    layouts = set(
        [
            "⿰",
            "⿱",
            "⿲",
            "⿳",
            "⿴",
            "⿵",
            "⿶",
            "⿷",
            "⿸",
            "⿹",
            "⿺",
            "⿻",
        ]
    )

    with open("./wordlists/IDS_dictionary.txt", "r", encoding="utf-8") as fread:
        lines = fread.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # print(line)
            head, expression = line.split(":")

            if not rad_db.is_radical_variant(head):
                char_decompositions[head] = expression

            else:
                print(f"{head} is a radical already")
                radical_found.add(head)
                radical_norminal_found.add(rad_db.norminal(head))

            if len(expression) < 2:
                print(f"Single {head}\t{expression}")

            pass

        for key in char_decompositions:
            components = char_decompositions[key].split(" ")

            for comp in components:
                if not comp:
                    continue

                if (
                    comp not in layouts
                    and comp not in char_decompositions
                    and not rad_db.is_radical_variant(comp)
                    and comp[0] != "&"
                ):
                    non_rad_components.setdefault(comp, set())
                    non_rad_components[comp].add(head)

    print("Non-radical tokens found")
    print("\n".join(sorted(non_rad_components.keys())))
    pass

    full_char_decompositions = char_decompositions

    round = [0, 0, 0]

    # Replaces 2 times to make sure all items are replaced
    for i in range(0, 3):
        for key in full_char_decompositions:
            expression = full_char_decompositions[key]
            matches = regex.findall(PATTERN_ZH, expression)
            changed = False

            for char in matches:
                if char in full_char_decompositions:
                    sub = full_char_decompositions[char]
                    if sub == char:
                        continue

                    round[i] += 1
                    # print(f"{key}: {char} => {sub}")
                    changed = True

                    expression = expression.replace(char, sub)

            full_char_decompositions[key] = expression

            pass

    print(round)

    rads = Radicals()
    rads.load_radical_data()

    # Radical standalone form will has its decomposition as it's norminal form
    for rad in rads.radical_list:
        info = rads.lookup(rad)
        if info["standalone"]:
            full_char_decompositions[info["standalone"]] = rads.norminal(rad)

    with open("./wordlists/IDS_dictionary_radical_perfect.txt", "w", encoding="utf-8") as fwrite:
        items = full_char_decompositions.items()

        for head, expression in items:
            fwrite.write(f"{head}:{expression}\n")
