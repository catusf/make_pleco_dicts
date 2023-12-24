import hanzidentifier
import os
import re
import urllib.parse
import json


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
PC_TRIANGLE = "▶"  # ►
PC_DIAMOND_SUIT = "♦"
PC_HEART_SUIT = "♥"
PC_CLUB_SUIT = "♣"
PC_SPADE_SUIT = "♠"


def headword_to_url(word):
    quoted = urllib.parse.quote(word, encoding="utf-8", errors="replace")
    return f"https://hanzii.net/search/word/{quoted}?hl=vi"


def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


def pure_traditional(word):
    return hanzidentifier.is_traditional(word) and not hanzidentifier.is_simplified(
        word
    )


def get_chinese_words(text):
    headwords = re.findall(PATTERN_ZH, text, flags=re.DOTALL)

    return [word for word in headwords if hanzidentifier.is_simplified(word)]


def url_to_headword(url):
    match = re.search(PATTERN_URL, url)

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
    return re.sub(PATTERN_REDUNDANT, "", text).replace("''", "'")


def remove_chinese_bracket(text):
    return re.sub("【(.+?)】", r"\1", text)


def remove_traditional_text(text):
    return re.sub("【.+?】", "", text)


def remove_see_more_examples(text):
    return re.sub("Xem thêm \d+ ví dụ nữa", "", text)


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
