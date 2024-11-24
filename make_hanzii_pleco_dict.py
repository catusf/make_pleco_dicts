import sys
import json
import signal
import argparse
from os.path import join
import datetime
import readchar
from tools_configs import *


def keyboard_handler(signum, frame):
    msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
    print(msg, end="", flush=True)
    res = readchar.readchar()
    if res == "y":
        sys.exit(1)
    else:
        print("", end="\r", flush=True)
        print(" " * len(msg), end="", flush=True)  # clear the printed line
        print("    ", end="\r", flush=True)


MAKE_PLECO = False


def main():
    parser = argparse.ArgumentParser(description="Dictionary processing tool")
    parser.add_argument(
        "--dict-size",
        choices=["small", "mid", "big"],
        default="small",
        required=False,
        help="Dictionary size: 'small' for Vietnamese definitions, 'mid' for definitions and examples, 'big' for all definitions including Chinese.",
    )
    args = parser.parse_args()

    dict_size = args.dict_size

    now_datetime = datetime.datetime.now()
    now_str = now_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    signal.signal(signal.SIGINT, keyboard_handler)

    print("Open new recommendation file")
    with open(join(DATA_DIR, "new_reccommendations.json"), "r", encoding="utf-8") as fread:
        new_recomend = json.load(fread)

    print("Open dictionary data file")
    with open(join(DATA_DIR, "dict_data.json"), "r", encoding="utf-8") as fread:
        dict_data = json.load(fread)

    this_dic_words_set = set(load_frequent_words("dic_words_set.txt"))
    current_word_list = this_dic_words_set

    PC_DICT_NAME = "//Trung-Viet Beta Dict"
    # MAX_ITEMS = 1000000
    MAX_ITEMS = 100

    with open(join(DICT_DIR, "tvb_pleco.txt"), "w", encoding="utf-8") as pleco_import_file:
        if MAKE_PLECO:
            pleco_import_file.write(f"{PC_DICT_NAME}\n")

        for num, headword in enumerate(sorted(dict_data)):
            dict_item = dict_data[headword]

            if num >= MAX_ITEMS:
                break

            print(f"Processing {num+1}: {headword}...")
            pleco_string = ""

            if headword not in current_word_list:
                print(f"Item not in current_word_list: {headword}")
                # continue

            pleco_string += f"{dict_item['chinese']}\t"

            if MAKE_PLECO:
                f"{dict_item['pinyin']}\t"

            if dict_item["amhanviet"]:
                pleco_string += f"{pleco_make_dark_gray(pleco_make_bold(dict_item['amhanviet'], make_pleco=MAKE_PLECO), make_pleco=MAKE_PLECO)}\n"
                # pleco_string += f"{pleco_make_dark_gray(pleco_make_bold(PC_HANVIET_MARK))} {pleco_make_italic(dict_item['amhanviet'])}\n"

            # if dict_size in ['mid', 'big'] and dict_item['amhanviet']:
            # if dict_size == 'big':
            for wordkind in dict_item["wordkinds"]["list_items"]:
                # pleco_string += f"{pleco_make_dark_gray(pleco_make_bold(wordkind))}\n"

                items = dict_item["wordkinds"]["list_items"][wordkind]
                for item in items:
                    if len(items) > 1:
                        number = number_in_cirle(int(item["definition"]["number"]))
                        pleco_string += f"{pleco_make_dark_gray(pleco_make_bold(number,make_pleco=MAKE_PLECO),
                                                                make_pleco=MAKE_PLECO)} "

                    if dict_size == "big":
                        pleco_string += f"{pleco_make_blue(item['definition']['chinese'], make_pleco=MAKE_PLECO)} "

                    pleco_string += f"{item['definition']['vietnamese']}\n"

                    example = item["definition"]["example"]

                    if dict_size in ["mid", "big"]:
                        pleco_string += (
                            f"{pleco_make_dark_gray(PC_DIAMOND + " " + PC_VIDU_NEW_MARK, make_pleco=MAKE_PLECO)}\n "
                        )
                        pleco_string += f"{pleco_make_blue(example['example_chinese'], make_pleco=MAKE_PLECO)} "
                        pleco_string += f"{pleco_make_italic(example['example_pron'], make_pleco=MAKE_PLECO)} "
                        pleco_string += f"{example['example_meaning']}\n"

                    if reccs := new_recomend[headword] and dict_size in ["big"]:
                        pleco_string += f"\n{pleco_make_dark_gray(
                            PC_CLUB_SUIT, make_pleco=MAKE_PLECO)} {pleco_make_dark_gray(PC_RELATED_MARK, make_pleco=MAKE_PLECO)}\n"

                        for rec in reccs:
                            key = list(rec.keys())[0]

                            item = rec[key]

                            # print(f"{key} {item['mean']} {item['pinyin']}")

                            if key in dict_data:
                                pleco_string += f"{pleco_make_dark_gray(PC_ARROW, make_pleco=MAKE_PLECO)} {pleco_make_link(key, make_pleco=MAKE_PLECO)} {
                                    pleco_make_italic(item['pinyin'], make_pleco=MAKE_PLECO)} {item['mean']}\n"
                            else:
                                pleco_string += f"{pleco_make_dark_gray(PC_ARROW, make_pleco=MAKE_PLECO)} {pleco_make_blue(key, make_pleco=MAKE_PLECO)} {
                                    pleco_make_italic(item['pinyin'])} {item['mean']}\n"

            pleco_string = pleco_string.replace("\n\n", "\n")
            pleco_string = pleco_make_new_line(pleco_string)
            pleco_import_file.write(f"{pleco_string}\n")

    later_datetime = datetime.datetime.now()
    print(f"Time elapsed {later_datetime-now_datetime}")


if __name__ == "__main__":
    main()
