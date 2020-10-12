ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
assert len(ALPHABET) == 33
assert len(set(ALPHABET)) == 33


def split_by_length(words):
    result = {}
    for w in words:
        if len(w) not in result:
            result[len(w)] = []
        result[len(w)].append(w)
    return result


def letterset(word):
    return ''.join(sorted(set(word)))


def lettermask(word):
    bn = ''.join(('1' if ch in word else '0') for ch in ALPHABET)
    return int(bn, base=2)


def popcount(mask):
    return bin(mask)[2:].count('1')
