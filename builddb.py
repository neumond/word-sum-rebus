import re
import random

WORD_RE = re.compile(r'^[а-яё]+$')
VOWEL_RE = re.compile(r"[аоуыэяюёие]'?")


def get_stress_form(w):
    result = ''
    for vm in VOWEL_RE.finditer(w):
        if vm.group(0).endswith("'"):
            result += '#'
        else:
            result += '.'
    return result


BEN_FORM = get_stress_form("бенеди'кт")
CUM_FORM = get_stress_form("камбербе'тч")


def build():
    ben_words = []
    cum_words = []

    with open('base.txt', 'r', encoding='cp1251') as f:
        for line in f:
            line = line.rstrip('\n\r ')
            if not line:
                # article split
                continue
            if line.startswith(' '):
                # word variation
                continue
            if line.startswith('*'):
                # not used words
                continue
            # print(line)
            word, flags, stress = line.split(' | ')[:3]

            if WORD_RE.fullmatch(word) is None:
                continue

            flags = set(flags.split(' '))
            if 'сущ' not in flags:
                continue
            if 'ед' not in flags:
                continue

            # print(word, flags, stress)
            sf = get_stress_form(stress)

            if sf == BEN_FORM and word.startswith('б'):
                ben_words.append(word)
            elif sf == CUM_FORM and word.startswith('к'):
                cum_words.append(word)

    return ben_words, cum_words


def generate(ben_words, cum_words):
    print(random.choice(ben_words), random.choice(cum_words))


b, c = build()
# print(len(b), len(c))
for i in range(50):
    generate(b, c)

# print(get_stress_form('команди\'р'))
