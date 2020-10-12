import re

from utils import ALPHABET


WORD_RE = re.compile(r'^[' + ALPHABET + r']+$')


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

            if len(set(word)) > 10:
                continue

            result.append(word)
    return sorted(set(result))


def create_word_database(words):
    with open('words.txt', 'w') as f:
        for w in words:
            f.write(w + '\n')


# create_word_database(build())
