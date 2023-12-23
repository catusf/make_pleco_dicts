import hanzidentifier
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import re
import urllib
import time
import os
import glob
import json

from tools_configs import *

# with open('words_to_add.txt', 'r', encoding='utf-8') as fin:
#     words_to_add = [line.strip() for line in fin.readlines()]

# words_to_add = load_frequent_words('red.txt')
# words_to_add = load_frequent_words('words_to_add.txt')
words_to_redownload = load_frequent_words('redownload.txt')

# with open(TOP_WORDS_24K, 'w', encoding='utf-8') as fout:
#     json.dump(top_words_24k, fout, indent = 4)

# with open(TOP_WORDS_24K, 'r', encoding='utf-8') as fin:
#     top_words_24k = json.load(fin)

list_to_read = words_to_redownload

# instantiate options
options = webdriver.ChromeOptions()

# run browser in headless mode
options.headless = True

# load website
url = 'https://hanzii.net/search/word/%E4%BA%BA?hl=vi'

# get the entire website content


print(f'{len(list_to_read)=}')

done_urls = set()
# new_urls = set()
new_urls = set([headword_to_url(word) for word in list_to_read])

# https://hanzii.net/search/word/%E4%BA%BA%E5%A4%AB?hl=vi

files = glob.glob(f'{HTML_FOLDER}/*.html')
print(f'There are existing {len(files)} files')

files_checked = set()
broken_files = list()
has_nodef_files = list()

trad_count = 0

find_all_chenese = True

for num, filepath in enumerate(files):
    headword, ext = os.path.splitext(os.path.split(filepath)[1])
    # filename = f'{HTML_FOLDER}/{headword}.html'
    url = headword_to_url(headword)

    # if not hanzidentifier.is_simplified(headword):
    #     trad_count += 1
    #     print(f'Traditional {headword}')
    #     os.remove(filepath)
    #     new_urls.remove(url)

    #     continue
    check_file_exists = True

    if check_file_exists:
        if is_non_zero_file(filepath):
            done_urls.add(url)

            if url in new_urls:
                new_urls.remove(url)

            # See if file contains any new words

            check_file_contents = False

            if check_file_contents:

                if filepath not in files_checked:
                    with open(filepath, 'r', encoding='utf-8') as fin:
                        html = fin.read()
                        files_checked.add(filepath)

                        if html.find(MARKER_GOOD_FILE) == -1:
                            broken_files.append(filepath)

                        if html.find(MARKER_HAS_DEF_FILE) == -1:
                            has_nodef_files.append(filepath)

                        if find_all_chenese:
                            chinese_words = get_chinese_words(html)

                            for headword in chinese_words:
                                url = headword_to_url(headword)

                                if url not in done_urls:
                                    new_urls.add(url)

                    if num % 100 == 0:
                        print(
                            f'File num {num} urls {len(new_urls)=} {len(broken_files)=} {len(has_nodef_files)=}')

        else:
            new_urls.add(url)

    else:
        new_urls.add(url)

with open('broken_file_list.txt', 'w', encoding='utf-8') as fout:
    fout.writelines([(line + '\n') for line in broken_files])

with open('has_nodef_list.txt', 'w', encoding='utf-8') as fout:
    fout.writelines([(line + '\n') for line in has_nodef_files])

print(f'Traditional count {trad_count}')

# to_remove = []
# for url in new_urls:
#     headword = url_to_headword(url)

#     if not hanzidentifier.is_simplified(headword):
#         to_remove.append(url)

# for url in to_remove:
#     new_urls.remove(url)

print(f'{len(new_urls)=}')

if not new_urls:
    print('No more urls to search')
    exit(0)

# instantiate driver
driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()), options=options)

new_urls_list = list(new_urls)

# count = 0
while True and len(new_urls_list) > 0:
    url = new_urls.pop()
    headword = url_to_headword(url)

    if not headword:
        print('Wrong headword {headword}')
        continue

    filename = f'{headword}.html'

    html = ''
    if is_non_zero_file(filename):
        print(f'Restoring {headword}')
        with open(filename, 'r', encoding='utf-8') as fin:
            html = fin.read()
    else:
        print(f'Downloading {headword}')
        driver.get(url)
        time.sleep(WAIT_TIME)

        html = driver.page_source
        done_urls.add(url)

        with open(os.path.join(HTML_FOLDER, filename), 'w', encoding='utf-8') as fout:
            fout.write(html)

    if not new_urls:
        print('No more urls to search')
        break

    print(f'=== Current Done {len(done_urls)} and New {len(new_urls)}')
