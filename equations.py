import re
from itertools import (
    combinations,
    combinations_with_replacement,
    islice,
    permutations,
)

from tqdm import tqdm

ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
assert len(ALPHABET) == 33
assert len(set(ALPHABET)) == 33
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


def split_by_length(words):
    result = {}
    for w in words:
        if len(w) not in result:
            result[len(w)] = []
        result[len(w)].append(w)
    return result


def patternize(word, skip=' '):
    used = {}
    result = []
    alloc = iter('ABCDEFGHIJ')
    for s in word:
        if s not in skip:
            if s not in used:
                used[s] = next(alloc)
            result.append(used[s])
        else:
            result.append(s)
    return ''.join(result)


def letterset(word):
    return ''.join(sorted(set(word)))


def lettermask(word):
    bn = ''.join(('1' if ch in word else '0') for ch in ALPHABET)
    return int(bn, base=2)


def popcount(mask):
    return bin(mask)[2:].count('1')


class LetterMaskIndex:
    def __init__(self, words):
        self._index = {}
        for w in words:
            mask = lettermask(w)
            if mask not in self._index:
                self._index[mask] = []
            self._index[mask].append(w)

        self._match_cache = {}

    def search_submatches(self, word):
        lmask = lettermask(word)
        assert popcount(lmask) <= 10

        if lmask not in self._match_cache:
            mc = []
            for wmask in self._index.keys():
                if popcount(wmask | lmask) <= 10:
                    mc.append(wmask)
            self._match_cache[lmask] = mc

        for wmask in self._match_cache[lmask]:
            yield from iter(self._index[wmask])


def attempt_to_match(a, b, s):
    assert len(a) == len(b)
    assert len(a) <= len(s) <= len(a) + 1

    all_chars = letterset(a + b + s)
    assert len(all_chars) <= 10

    match = None
    for x in permutations('0123456789', len(all_chars)):
        mp = {ch: n for ch, n in zip(all_chars, x)}

        at = ''.join(mp[ch] for ch in a)
        if at[:1] == '0':
            continue
        at = int(at)

        bt = ''.join(mp[ch] for ch in b)
        if bt[:1] == '0':
            continue
        bt = int(bt)

        st = ''.join(mp[ch] for ch in s)
        if st[:1] == '0':
            continue
        st = int(st)

        if at + bt != st:
            continue

        if match is not None:
            return False, 'multiple matches'

        match = f'{at}+{bt}={st}'
    if match is not None:
        return True, match
    return False, 'no matches'


def solve_long1(words):
    # words = ['деталь', 'изделие']
    print('Total words:', len(words))

    mask_index_by_len = {
        wlen: LetterMaskIndex(wlist)
        for wlen, wlist in split_by_length(words).items()
    }

    c = 0
    pair_patterns = set()
    for a in tqdm(words):
        for b in mask_index_by_len[len(a)].search_submatches(a):
            if a > b:
                continue
            # 85M pairs here
            c += 1
            pair_patterns.add(patternize(f'{a}+{b}', '+'))

            # for s in mask_index_by_len[len(a)].search_submatches(a + b):
            #     # print('Attempt to match', a, b, s, end=': ')
            #     # success, reason = attempt_to_match(a, b, s)
            #     # print(success, reason)
            #     # assert len(letterset(a + b + s)) <= 10
            #     c += 1
            #
            # if (len(a) + 1) in mask_index_by_len:
            #     for s in mask_index_by_len[len(a) + 1].search_submatches(a + b):
            #         # print('Attempt to match', a, b, s, end=': ')
            #         # success, reason = attempt_to_match(a, b, s)
            #         # print(success, reason)
            #         # assert len(letterset(a + b + s)) <= 10
            #         c += 1

        # print(f'Word {i + 1}, possibles {c}, bc {bc}')
        # break
    print('Total pairs:', c)
    print('Unique pair patterns:', len(pair_patterns))


def create_word_database(words):
    # create_word_database(build())
    with open('words.txt', 'w') as f:
        for w in words:
            f.write(w + '\n')


def load_word_database():
    result = []
    with open('words.txt', 'r') as f:
        for line in f:
            result.append(line.strip())
    return result


def create_pair_database(words):
    # create_pair_database(load_word_database())
    from array import array
    from zlib import compress

    word_index = {w: i for i, w in enumerate(words)}
    mask_index_by_len = {
        wlen: LetterMaskIndex(wlist)
        for wlen, wlist in split_by_length(words).items()
    }

    c = 0
    chunks = []
    for a in tqdm(words):
        mids = array('l')
        for b in mask_index_by_len[len(a)].search_submatches(a):
            if a > b:
                continue
            c += 1
            mids.append(word_index[b])
        mids.append(-1)
        chunks.append(mids.tobytes())

    with open('pairs.zdt', 'wb') as f:
        f.write(compress(b''.join(chunks)))

    print('Total pairs:', c)


def iterate_pairs(words):
    from itertools import chain, repeat

    def file_chunks(f):
        from zlib import decompressobj
        d = decompressobj()
        while True:
            chunk = f.read(4096)
            if len(chunk):
                yield d.decompress(chunk)
            else:
                yield d.flush()
                break

    def stream_of_ints(fc):
        from array import array
        isize = array('l').itemsize
        buf = b''
        for chunk in fc:
            buf += chunk
            prepared = (len(buf) // isize) * isize
            if prepared > 0:
                assert prepared % isize == 0
                yield from iter(array('l', buf[:prepared]))
                buf = buf[prepared:]
        assert buf == b''

    aiter = chain(iter(words), repeat(None))
    a = next(aiter)
    with open('pairs.zdt', 'rb') as f:
        for i in stream_of_ints(file_chunks(f)):
            if i == -1:
                a = next(aiter)
            else:
                assert a is not None
                yield a, words[i]

    # 85297031 pairs


def iterate_with_sums(words, pair_iterator):
    mask_index_by_len = {
        wlen: LetterMaskIndex(wlist)
        for wlen, wlist in split_by_length(words).items()
    }

    for a, b in pair_iterator:
        c = 0
        for s in mask_index_by_len[len(a)].search_submatches(a + b):
            # print('Attempt to match', a, b, s, end=': ')
            # success, reason = attempt_to_match(a, b, s)
            # print(success, reason)
            # assert len(letterset(a + b + s)) <= 10
            yield a, b, s
            c += 1
        if (len(a) + 1) in mask_index_by_len:
            for s in mask_index_by_len[len(a) + 1].search_submatches(a + b):
                # print('Attempt to match', a, b, s, end=': ')
                # success, reason = attempt_to_match(a, b, s)
                # print(success, reason)
                # assert len(letterset(a + b + s)) <= 10
                c += 1
                yield a, b, s


# print(load_word_database()[:100])
# solve_long1(load_word_database())

# from itertools import islice
# from random import random
# words = load_word_database()
# c = 0
# for a, b, s in iterate_with_sums(
#     words,
#     iterate_pairs(words),
# ):
#     if random() < 0.0001:
#         c += 1
#         print(a, b, s)
#         if c > 100:
#             break
