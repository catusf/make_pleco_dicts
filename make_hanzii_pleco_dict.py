# %%
import sys
import json
import signal
import datetime
import readchar
# from bs4 import BeautifulSoup
from tools_configs import *
# import dicttoxml


def keyboard_handler(signum, frame):
    msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
    print(msg, end="", flush=True)
    res = readchar.readchar()
    if res == 'y':
        # print("")
        # print("Saving data and quiting...")
        # with open(f"dict_data.json", "w", encoding="utf-8") as fwrite:
        #     json.dump(dict_data, fwrite, indent=4, ensure_ascii=False)

        # print(" done.")

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

print('Open new recommendation file')
with open("new_reccommendations.json", "r", encoding="utf-8") as fread:
    new_recomend = json.load(fread)

print('Open dictionary data file')
with open("dict_data.json", "r", encoding="utf-8") as fread:
    dict_data = json.load(fread)

# print('Convert and write xml file')

# with open("dict_data.xml", "wb") as fwrite:
#     # xml = dicttoxml.dicttoxml(
#     #     dict((k, dict_data[k]) for k in extracted_keys if k in extracted_keys))
#     xml = dicttoxml.dicttoxml(dict_data)
#     fwrite.write(xml)

this_dic_words_set = set(load_frequent_words('dic_words_set.txt'))

current_word_list = this_dic_words_set  # top_words_24k

# Constant definitions

PC_DICT_NAME = "//Trung-Viet Beta Dict"

MAX_ITEMS = 100  # 20
MAX_ITEMS = 1000000  # 20

BIGNUM = 20000000

wordkinds_set = set()
wordkinds_actual_set = set()

pleco_import_file = open("tvb_pleco.txt", "w", encoding="utf-8")

pleco_import_file.write(f"{PC_DICT_NAME}\n")

freq = []


for num, headword in enumerate(sorted(dict_data)):
    dict_item = dict_data[headword]

    if num >= MAX_ITEMS:
        break

    print(f"Processing {num+1}: {headword}...")
    pleco_string = ""

    popularity = 0

    if headword not in current_word_list:
        print(f'Item not in current_word_list: {headword}')
        continue

    pleco_string += f"{dict_item['chinese']}\t{dict_item['pinyin']}\t"

    if dict_item['amhanviet']:
        pleco_string += f"{pleco_make_dark_gray(pleco_make_bold(PC_HANVIET_MARK))} {
            pleco_make_italic(dict_item['amhanviet'])}\n"

    # print(f'{chinese=} {pinyin=} {viet=}')

    for wordkind in dict_item['wordkinds']['list_items']:
        pleco_string += f"{pleco_make_dark_gray(pleco_make_bold(wordkind))}{
            PC_NEW_LINE}"

        for item in dict_item['wordkinds']['list_items'][wordkind]:
            pleco_string += f"\n{pleco_make_dark_gray(
                pleco_make_bold(number_in_cirle(int(item['definition']['number']))))} "
            pleco_string += (
                f"{pleco_make_blue(item['definition']['chinese'])} {
                    item['definition']['vietnamese']}\n"
            )
            example = item['definition']['example']

            if example:
                pleco_string += f"{pleco_make_dark_gray(PC_DIAMOND)} {
                    pleco_make_dark_gray(PC_VIDU_NEW_MARK)}\n "
                pleco_string += f"{pleco_make_blue(example['example_chinese'])} {pleco_make_italic(
                    example['example_pron'])} {example['example_meaning']}\n"

    reccs = new_recomend[headword]

    if reccs:
        pleco_string += f"\n{pleco_make_dark_gray(
            PC_CLUB_SUIT)} {pleco_make_dark_gray(PC_RELATED_MARK)}\n"

        for rec in reccs:
            key = list(rec.keys())[0]

            item = rec[key]

            # print(f"{key} {item['mean']} {item['pinyin']}")

            if key in dict_data:
                pleco_string += f"{pleco_make_dark_gray(PC_ARROW)} {pleco_make_link(key)} {
                    pleco_make_italic(item['pinyin'])} {item['mean']}\n"
            else:
                pleco_string += f"{pleco_make_dark_gray(PC_ARROW)} {pleco_make_blue(key)} {
                    pleco_make_italic(item['pinyin'])} {item['mean']}\n"

    pleco_string = pleco_string.replace("\n\n", "\n")
    pleco_string = pleco_string.replace("\n", PC_NEW_LINE)

    pleco_import_file.write(f"{pleco_string}\n")

pleco_import_file.close()

later_datetime = datetime.datetime.now()

print(f'Time elapsed {later_datetime-now_datetime}')
