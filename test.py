from tools_configs import Radicals

import hanzipy

from hanzipy.decomposer import HanziDecomposer

decomposer = HanziDecomposer()


decomposition = decomposer.decompose("圭", decomposition_type=2)
from pinyin import get as get_pinyin
from tools_configs import Radicals


radical_database = Radicals()
radical_database.load_radical_data()

radical_database.save_radical_data()

# print(radical_database.lookup("丷"))

# print(radical_database.is_radical_variant("丷"))

# print(radical_database.norminal("丷"))

rad_set = set()
py_set = set()
var_set = set()

for variant in decomposer.radicals:
    pinyin = get_pinyin(variant)
    radical = variant

    if variant == pinyin:
        if radical_database.is_radical_variant(variant):
            pinyin = radical_database.lookup(variant)["pinyin"]
            radical = radical_database.norminal(variant)

    # print(f"{rad} {radical} {pinyin}")
    if variant == pinyin:
        print(f"{variant}")
    else:
        # print(f"{variant} {radical} {pinyin}")
        rad_set.add(radical)
        var_set.add(variant)
        py_set.add(pinyin)

print(f"{len(radical_database.radicals())=}")
print(f"{len(radical_database.variants())=}")
print(f"{len(decomposer.radicals)=}")
print(f"{len(rad_set)=}")
print(f"{len(var_set)=}")
print(f"{len(py_set)=}")

rad_meanings = {}
count = 0
all = list()

for rad in radical_database.radicals():
    char = radical_database.lookup(rad)
    norm = radical_database.norminal(rad)
    variants = radical_database.get_variants(rad)
    # print(f'{norm} {char['pinyin']} {"-".join(variants)}')
    rad_meanings[rad] = char["pinyin"]
    count += len(variants)
    all.append(norm)
    all.extend(variants)
    if len(variants) != len(set(variants)):
        print(f"Duplicated: {norm} {variants}")


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set(x for x in seq if x in seen or seen_add(x))
    # turn the set into a list (as requested)
    return list(seen_twice)


all.sort()
unique = sorted(list(radical_database.variants()))

# print(list(next((idx, x, y) for idx, (x, y) in enumerate(zip(all, unique)) if x != y)))

print(f"{list_duplicates(all)}")

print(f"{count=}")

mine = set(radical_database.variants())
theirs = set(decomposer.radicals)

print(f"{theirs-mine=}")

# import json

# with open(r"C:\Python312\envs\pleco\Lib\site-packages\hanzipy-1.0.4-py3.12.egg\hanzipy\data\radical_with_pinyins.json", "w", encoding='utf-8') as fout:
#     json.dump(rad_meanings, fout, indent=4, ensure_ascii=False)
