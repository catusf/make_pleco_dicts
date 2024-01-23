import codecs
from tools_configs import build_ids_radical_perfect


def load_cedict(load_to_mongo=False):
    f = codecs.open(
        r"C:\Python312\envs\pleco\Lib\site-packages\hanzipy-1.0.4-py3.12.egg\hanzipy\data\cedict_ts.u8", "r", "utf8"
    )

    c = 0

    new_words = {}
    for line in f:
        if line.startswith("#"):
            continue
        trad, simp = line.split(" ")[:2]
        pinyin = line[line.find("[") + 1 : line.find("]")]
        eng = line[line.find("/") + 1 : line.rfind("/")]

        word = {"traditional": trad, "english": eng, "pinyin": pinyin}

        new_words[simp] = word

    f.close()

    return new_words


print("Loading words...")

words = load_cedict(load_to_mongo=False)

char_decompositions = {}

build_ids_radical_perfect()

with open("./wordlists/IDS_dictionary_radical_perfect.txt", "r", encoding="utf-8") as fread:
    lines = fread.readlines()

    for line in lines:
        head, decomp = line.strip().split(":")

        char_decompositions[head] = decomp.replace(" ", "")


print("Done! Loaded %d words." % len(words))

has_definitions = set(char_decompositions) & set(words)

print(f"No {len(has_definitions)=}")
