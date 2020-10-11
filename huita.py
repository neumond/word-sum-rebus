import random
import re

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


HUITA_FORM = get_stress_form("хуита'")


def build():
    result = []
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

            if sf == HUITA_FORM and word.endswith('та'):
                result.append(word)
    return result


ws = build()
# print(len(ws))
for w in ws:
    print(w)
# print(random.sample(ws, 10))
