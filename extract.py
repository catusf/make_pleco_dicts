# %%
import readchar
import time
import signal
from bs4 import BeautifulSoup
import sys
import glob
import json
from pinyin import get as pinyinget
import datetime
from tools_configs import *
import shutil
import re


def keyboard_handler(signum, frame):
    msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
    print(msg, end="", flush=True)
    res = readchar.readchar()
    if res == 'y':
        print("")
        print(f"Saving data and quiting {len(dict_data)} ...")
        with open(f"dict_data.json", "w", encoding="utf-8") as fwrite:
            json.dump(dict_data, fwrite, indent=4, ensure_ascii=False)

        print(" done.")

        sys.exit(1)
    else:
        print("", end="\r", flush=True)

        print(" " * len(msg), end="", flush=True)  # clear the printed line
        print("    ", end="\r", flush=True)


now_datetime = datetime.datetime.now()
now_str = now_datetime.strftime("%Y-%m-%d_%H-%M-%S")

# Utilities functions


signal.signal(signal.SIGINT, keyboard_handler)

NEED_CONVERT = r"([^	↑ ,; 0-9a-zA-Z()一-龥])"


with open(f"dict_data.json", "r", encoding="utf-8") as fread:
    dict_data = json.load(fread)

# The above code is likely defining a function or variable called "count_current_items" in the Python
# programming language. However, without seeing the actual code, it is not possible to determine the
# exact purpose or functionality of the code.
# count_current_items = len(dict_data)

# print(f'{count_current_items=}')

top_words_100k_index = {
    k: v for v, k in enumerate(load_frequent_words(TOP_WORDS_1M)[:100001])
}  # Only care about first 100000 words

top_words_24k_index = {k: v for v, k in enumerate(
    load_frequent_words(TOP_WORDS_24K))}

top_words_24k = set(load_frequent_words(TOP_WORDS_24K))

this_dic_words_set = set(load_frequent_words('dic_words_set.txt'))


current_word_list = this_dic_words_set  # top_words_24k

# Constant definitions

PC_DICT_NAME = "//Trung-Viet Dict"
PC_NEW_LINE = chr(0xEAB1)
PC_HANVIET_MARK = "HÁN VIỆT"
PC_GOIY_MARK = "LIÊN QUAN"
PC_VIDU_OLD_MARK = "Ví dụ:"
PC_VIDU_NEW_MARK = "VÍ DỤ"
PC_DIAMOND = "❖"
PC_ARROW = "»"
PC_TRIANGLE = "▶"  # ►
PC_DIAMOND_SUIT = "♦"
PC_HEART_SUIT = "♥"
PC_CLUB_SUIT = "♣"
PC_SPADE_SUIT = "♠"

MAX_ITEMS = 1000000  # 20
MAX_ITEMS = 100  # 20

files = glob.glob(f"{HTML_FOLDER}/人*.html")
files = glob.glob(f"{HTML_FOLDER}/*.html")
print(f'Number of existing files: {len(files)=}')

# files = glob.glob(f'{HTML_FOLDER}/人面.html')
filepath = f"{HTML_FOLDER}/点.html"
filepath = f"{HTML_FOLDER}/詗.html"
filepath = f"{HTML_FOLDER}/人.html"

wordkinds_set = set()
wordkinds_actual_set = set()

log_file = open(f"{now_str}-error.log", "w", encoding="utf-8")
pleco_import_file = open(f"{now_str}-hanzii_pleco.txt", "w", encoding="utf-8")

pleco_import_file.write(f"{PC_DICT_NAME}\n")

freq = []

# dict_data = {}

for num, filepath in enumerate(files):
    dict_item = None
    # No definitions	html\换.html

    # if filepath != 'html\〇.html':
    #     continue

    if num >= MAX_ITEMS:
        break

    print(f"Processing {num+1}: {filepath}...", end=" ")
    pleco_string = ""

    # The above code is not doing anything. It only contains the word "headword" and three hash
    # symbols, which are used to create comments in Python code.
    headword, ext = os.path.splitext(os.path.split(filepath)[1])

    popularity = 0

    # if headword not in this_dic_words_set:
    #     print(f'Not in this_dic_words_set')
    #     continue
    if headword in dict_data:
        print('Already in dict_data')
        continue
    else:
        print('New item')

    if headword in top_words_24k_index:
        popularity = top_words_24k_index[headword]
    elif headword in top_words_100k_index:
        popularity = top_words_100k_index[headword]
    else:
        popularity = BIGNUM  # No need to include in dictionary
        # continue # Runs this means limits to to24k
    # continue

    if headword not in current_word_list and headword:
        continue

    # url = headword_to_url(headword)

    with open(filepath, "r", encoding="utf-8") as fin:
        html = fin.read()

    soup = BeautifulSoup(html, features='lxml')

    content_result = soup.find("div", class_="content-result")

    if not content_result:
        log_file.write(f"No content_result \t{filepath}\n")
        continue

    reccom_words_soup, word_detail_soup, hot_keywords_soup = list(
        content_result.next.children
    )

    # Process Chi tiết từ
    if not (char_pron_soup := word_detail_soup.find("div", class_="box-word")):
        print(f"{filepath=} has no character pronunciation")
        log_file.write(f"No pronunciation\t{filepath}\n")

        continue

    chinese_word = (
        ""
        if not (
            chinese_word_soup := char_pron_soup.find(
                "span", class_="simple-tradition-wrap"
            )
        )
        else remove_traditional_text(chinese_word_soup.text)
    )

    pinyin_pron = (
        ""
        if not (pinyin_pron_soup := char_pron_soup.find("span", class_="txt-pinyin"))
        else pinyin_pron_soup.text[1:-1].lower()
    )

    amhanviet = (
        ""
        if not (amhanviet_soup := char_pron_soup.find("span", class_="txt-cn_vi"))
        else amhanviet_soup.text[1:-1].lower()
    )

    if not chinese_word_soup:

        log_file.write(f"No Chinese characters\t{filepath}\n")
        continue

    chinese_word = remove_redundant_characters(chinese_word)
    pinyin_pron = remove_redundant_characters(pinyin_pron)

    hanzii_popularity = str(BIGNUM) if not (hanzii_pop_soup := soup.find(
        'div', class_='popularity-box')) else hanzii_pop_soup.find('span').text
    hanzii_popularity = hanzii_popularity.replace('#', '')
    dict_item = {
        "chinese": chinese_word,
        "pinyin": pinyin_pron,
        "amhanviet": amhanviet,
        "popularity": popularity,
        "hz_popularity": hanzii_popularity,
    }

    pleco_string += f"{chinese_word}\t{pinyin_pron}\t"

    if amhanviet:
        pleco_string += f"{pleco_make_dark_gray(pleco_make_bold(PC_HANVIET_MARK))} {pleco_make_italic(amhanviet)}{PC_NEW_LINE}"

    # print(f'{chinese=} {pinyin=} {viet=}')

    wordkind_list = [
        item.text.strip()
        for item in word_detail_soup.find_all("span", class_="word-kind")
    ]

    dict_item["wordkinds"] = {}
    dict_item["wordkinds"]["list_text"] = wordkind_list
    dict_item["wordkinds"]["list_items"] = {}
    dict_item["recommedations"] = []

    for wordkind in wordkind_list:
        wordkinds_set.add(wordkind)

    wordkinds_soups = word_detail_soup.find_all("div", class_="box-content")

    if not wordkinds_soups:
        single_def_soup = word_detail_soup.find(
            "div", class_="detail-word content-result-white")
        if not single_def_soup:
            log_file.write(f"No wordkinds_soups\t{filepath}\n")
            continue
        else:
            number = 1
            mean_chinese = single_def_soup.find(
                'span', class_='simple-tradition-wrap').text.strip()
            mean_viet = single_def_soup.find(
                'div', class_='txt-mean').text.strip()
            mean_chinese = remove_redundant_characters(
                remove_traditional_text(mean_chinese))
            mean_viet = remove_redundant_characters(mean_viet)

            if hanzidentifier.is_simplified(mean_viet):
                log_file.write(f"No Vietnamese definitions\t{filepath}\n")
                continue
            else:
                def_data = {
                    "definition": {
                        "number": number,
                        "vietnamese": mean_viet,
                        "chinese": mean_chinese,
                    }
                }
                def_data["definition"]["example"] = ''
                dict_item["wordkinds"]["list_items"][''] = []
                dict_item["wordkinds"]["list_items"][''].append(def_data)
    else:
        for wordkind_soup in wordkinds_soups:
            wordkind_text = (
                wordkind_soup.div.text.strip()
                if (wordkind_text_soup := wordkind_soup.find("div", class_="kind-word"))
                else "/".join(wordkind_list)
            )

            wordkind_text = wordkind_text.upper()

            wordkinds_actual_set.add(wordkind_text)

            dict_item["wordkinds"]["list_items"][wordkind_text] = []

            pleco_string += (
                f"{pleco_make_dark_gray(pleco_make_bold(wordkind_text))}{PC_NEW_LINE}"
            )
            # print(f'## {tuloai_text}')

            definitions_soup = wordkind_soup.find_all(
                "div", class_="item-content")

            if not definitions_soup:
                log_file.write(f"No definitions_soup\t{filepath}\n")
                continue

            for num, definition_soup in enumerate(definitions_soup):
                # print(definition.text)

                number = definition_soup.find(
                    "div", class_="icon-dot").text.strip()[:-1]
                mean_viet = definition_soup.find(
                    "span", class_="simple-tradition-wrap"
                ).text

                mean_chinese = (
                    ""
                    if not (
                        mean_chinese_soup := definition_soup.find(
                            "div", class_="txt-mean-explain"
                        )
                    )
                    else mean_chinese_soup.text
                )

                mean_chinese = remove_redundant_characters(
                    remove_traditional_text(mean_chinese))
                mean_viet = remove_redundant_characters(mean_viet)

                pleco_string += f"{PC_NEW_LINE}{pleco_make_dark_gray(pleco_make_bold(number_in_cirle(num+1)))} "
                pleco_string += (
                    f"{pleco_make_blue(mean_chinese)} {mean_viet}{PC_NEW_LINE}{PC_NEW_LINE}"
                )

                example_data = {"example": {}}

                if (
                    example_soup := definition_soup.find("div", class_="box-example")
                ) and example_soup.find("p", class_="ex-word"):
                    example_chinese = example_soup.find(
                        "p", class_="ex-word").text

                    example_pron = example_soup.find(
                        "p", class_="ex-phonetic").text
                    example_meaning = example_soup.find(
                        "p", class_="ex-mean").text

                    example_chinese = remove_redundant_characters(
                        remove_traditional_text(example_chinese)
                    )
                    example_pron = remove_redundant_characters(example_pron)
                    example_meaning = remove_redundant_characters(
                        example_meaning)

                    pleco_string += f"{pleco_make_dark_gray(PC_DIAMOND)} {pleco_make_dark_gray(PC_VIDU_NEW_MARK)}{PC_NEW_LINE} "
                    pleco_string += f"{pleco_make_blue(example_chinese)} {pleco_make_italic(example_pron)} {example_meaning}{PC_NEW_LINE}{PC_NEW_LINE}"

                    example_data = {
                        "example": {
                            "example_chinese": example_chinese,
                            "example_pron": example_pron,
                            "example_meaning": example_meaning,
                        }
                    }
                def_data = {
                    "definition": {
                        "number": number,
                        "vietnamese": mean_viet,
                        "chinese": mean_chinese,
                    }
                }
                def_data["definition"]["example"] = example_data["example"]
                dict_item["wordkinds"]["list_items"][wordkind_text].append(
                    def_data)

    recommendations_soup = reccom_words_soup.find_all("div", class_="box-item")
    pleco_string += f"{PC_NEW_LINE}{PC_NEW_LINE}{pleco_make_dark_gray(PC_CLUB_SUIT)} {pleco_make_dark_gray(PC_GOIY_MARK)}{PC_NEW_LINE}"

    dict_data[headword] = dict_item

    for recommendation_soup in recommendations_soup:

        reccomendation_mean = recommendation_soup.find(
            "div", class_="box-mean").text

        reccomendation_chinese = recommendation_soup.find(
            "span", class_="simple-tradition-wrap"
        ).text

        reccomendation_pinyin = (
            pinyinget(reccomendation_chinese)
            if not (
                rec_pinyin_s := recommendation_soup.find("div", class_="txt-pinyin")
            )
            else recommendation_soup.find("div", class_="txt-pinyin").text
        )

        reccomendation_chinese = remove_traditional_text(
            reccomendation_chinese)
        reccomendation_pinyin = remove_chinese_bracket(
            reccomendation_pinyin.lower())

        reccomendation_item = {'chinese': reccomendation_chinese,
                               'pinyin': reccomendation_pinyin,
                               'mean': reccomendation_mean
                               }

        if reccomendation_chinese == chinese_word:
            continue

        dict_item["recommedations"].append(reccomendation_item)

        pleco_string += f"{pleco_make_dark_gray(PC_ARROW)} {pleco_make_blue(reccomendation_chinese)} {pleco_make_italic(reccomendation_pinyin)} {reccomendation_mean}{PC_NEW_LINE}{PC_NEW_LINE}"

    pleco_string = pleco_string.replace("\n", PC_NEW_LINE)

    pleco_import_file.write(f"{pleco_string}\n")

    if num % 100:
        log_file.flush()
        pleco_import_file.flush()

log_file.close()

pleco_import_file.close()

with open(f"dict_data.json", "w", encoding="utf-8") as fwrite:
    json.dump(dict_data, fwrite, indent=4, ensure_ascii=False)

# print(f'New items: {len(dict_data)-count_current_items}')
print(f'New total: {len(dict_data)}')

with open(f"{now_str}_wordkinds.json", "w", encoding="utf-8") as fwrite:
    json.dump(list(wordkinds_actual_set), fwrite, indent=4, ensure_ascii=False)

later_datetime = datetime.datetime.now()

print(f'Time elapsed {later_datetime-now_datetime}')
# with open('freq.txt', 'w', encoding='utf-8') as freq_file:
#     freq_file.writelines([f'{x}\n' for x in freq])

# print(wordkinds_set)

# print(wordkinds_actual_set)

"""
https://plecoforums.com/threads/multiple-new-lines-in-user-defined-flashcards.5916/#post-44863

|2756| Diamond
EAB1 = new line
EAB2/EAB3 = bold
EAB4/EAB5 = italic
EAB8/EABB = "copy-whatever's-in-this-to-the-Input-Field hyperlinks"
coloured text:
"EAC1 followed by two characters with the highest-order bit 1 and the lowest-order 12 bits representing the first/second halves of a 24-bit RGB color value to start the range, EAC2 to end. So to render a character in green, for example, you'd want EAC1 800F 8F00, then the character, then EAC2."
---
UTF-8: U+EAB1 = '\xee\xaa\xb1'


EAB2/EAB3 = bold
EAB4/EAB5 = italic

eabe ... eabf: Bold
eab8 ... eabb|: Hyperlink

一		one |2756| floor; ceiling|eab1| |eab1||eabe|PINYIN|eabf| y|12b||eab1| |eab1||eabe|FRAME|eabf| 1, |eabe|LESSON|eabf| 1, |eabe|BOOK|eabf| 1, |eabe|PAGE|eabf|  19|eab1| |eab1||eabe|NAVIGATION|eabf| ↑Lesson 1↑ (|eab8|本书1第1课|eabb|) |bb|two|bb| (|eab8|二|eabb|)|eab1| |eab1||eabe|SUBTLEX|eabf| |eab8|一|eabb|, |eab8|一个|eabb|, |eab8|一起|eabb|, |eab8|一样|eabb|, |eab8|一下|eabb|, |eab8|一直|eabb|, |eab8|一切|eabb|, |eab8|一点|eabb|, |eab8|一定|eabb|, |eab8|第一|eabb|, |eab8|一些|eabb|, |eab8|唯一|eabb|, |eab8|一会儿|eabb|, |eab8|一旦|eabb|, |eab8|之一|eabb|, |eab8|一半|eabb|, |eab8|一边|eabb|, |eab8|一般|eabb|, |eab8|一生|eabb|, |eab8|一刻|eabb|, |eab8|一辈子|eabb|, |eab8|一一|eabb|, |eab8|一致|eabb|, |eab8|一会|eabb|, |eab8|一路|eabb|, |eab8|万一|eabb|, |eab8|一分|eabb|, |eab8|一点儿|eabb|, |eab8|一团糟|eabb|, |eab8|一整天|eabb|, |eab8|一面|eabb|, |eab8|一百|eabb|, |eab8|一无所知|eabb|, |eab8|一两|eabb|, |eab8|进一步|eabb|, |eab8|一家|eabb|, |eab8|一百万|eabb|, |eab8|一时|eabb|, |eab8|一千|eabb|, |eab8|一模一样|eabb|, |eab8|一阵子|eabb|, |eab8|一向|eabb|, |eab8|一共|eabb|, |eab8|一阵|eabb|, |eab8|同一个|eabb|, |eab8|一万|eabb|, |eab8|一番|eabb|, |eab8|以防万一|eabb|, |eab8|一下子|eabb|, |eab8|星期一|eabb|, |eab8|一无所有|eabb||eab1| |eab1||eabe|OLDHSK|eabf| |eab8|第(第一)|eabb|, |eab8|一|eabb|, |eab8|一般|eabb|, |eab8|一边|2026|一边|2026||eabb|, |eab8|一点儿|eabb|, |eab8|一定|eabb|, |eab8|一共|eabb|, |eab8|一会儿|eabb|, |eab8|一|2026|就|2026||eabb|, |eab8|一块儿|eabb|, |eab8|一起|eabb|, |eab8|一切|eabb|, |eab8|一下儿|eabb|, |eab8|一些|eabb|, |eab8|一样|eabb|, |eab8|一|2026|也|2026||eabb|, |eab8|一直|eabb|, |eab8|不一定|eabb|, |eab8|差一点儿|eabb|, |eab8|进一步|eabb|, |eab8|统一|eabb|, |eab8|一|eabb|, |eab8|一半|eabb|, |eab8|一边|eabb|, |eab8|一道|eabb|, |eab8|一方面|2026|一方面|2026||eabb|, |eab8|一齐|eabb|, |eab8|一生|eabb|, |eab8|一时|eabb|, |eab8|一同|eabb|, |eab8|一下子|eabb|, |eab8|一致|eabb|, |eab8|一|2026|也|eabb|, |eab8|有(一)点儿|eabb|, |eab8||2026|之一|eabb|, |eab8|万一|eabb|, |eab8|一一|eabb|, |eab8|一带|eabb|, |eab8|一路平安|eabb|, |eab8|一路顺风|eabb|, |eab8|一面|2026|一面|eabb|, |eab8|一系列|eabb|, |eab8|一下儿|eabb|, |eab8|一向|eabb|, |eab8|一再|eabb|, |eab8|一阵|eabb|, |eab8|一口气|eabb|, |eab8|一连|eabb|, |eab8|一旁|eabb|, |eab8|一心|eabb|, |eab8|一行|eabb|, |eab8|有(一)些|eabb|, |eab8|这样一来|eabb|, |eab8|老一辈|eabb|, |eab8|同一|eabb|, |eab8|唯一|eabb|, |eab8|一辈子|eabb|, |eab8|一旦|eabb|, |eab8|一度|eabb|, |eab8|一概|eabb|, |eab8|一概而论|eabb|, |eab8|一个劲儿|eabb|, |eab8|一贯|eabb|, |eab8|一哄而散|eabb|, |eab8|一会儿|2026|一会儿|eabb|, |eab8|一技之长|eabb|, |eab8|一律|eabb|, |eab8|一帆风顺|eabb|, |eab8|一干二净|eabb|, |eab8|一举|eabb|, |eab8|一毛不拔|eabb|, |eab8|一身|eabb|, |eab8|一手|eabb|, |eab8|一头|eabb||eab1| |eab1||eabe|HSK|eabf| |eab8|一|eabb|, |eab8|一点儿|eabb|, |eab8|第一|eabb|, |eab8|一起|eabb|, |eab8|一下|eabb|, |eab8|一般|eabb|, |eab8|一边|eabb|, |eab8|一定|eabb|, |eab8|一共|eabb|, |eab8|一会儿|eabb|, |eab8|一样|eabb|, |eab8|一直|eabb|, |eab8|一切|eabb|, |eab8|统一|eabb|, |eab8|万一|eabb|, |eab8|唯一|eabb|, |eab8|一辈子|eabb|, |eab8|一旦|eabb|, |eab8|一律|eabb|, |eab8|一再|eabb|, |eab8|一致|eabb|, |eab8|不屑一顾|eabb|, |eab8|一度|eabb|, |eab8|一帆风顺|eabb|, |eab8|一贯|eabb|, |eab8|一举两得|eabb|, |eab8|一流|eabb|, |eab8|一目了然|eabb|, |eab8|一如既往|eabb|, |eab8|一丝不苟|eabb|, |eab8|一向|eabb||eab1|


"""
