from tqdm import tqdm

from utils import lettermask, popcount, split_by_length


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


def load_word_database():
    import gzip

    result = []
    with gzip.open('words.txt.gz', 'rt', encoding='utf-8') as f:
        for line in f:
            result.append(line.strip())
    return result


def iterate_pairs(words):
    # 85297031 pairs
    mask_index_by_len = {
        wlen: LetterMaskIndex(wlist)
        for wlen, wlist in split_by_length(words).items()
    }

    for a in tqdm(words):
        # if a <= 'азартность':
        #     continue
        if len(a) < 10:
            continue
        for b in mask_index_by_len[len(a)].search_submatches(a):
            if a > b:
                continue
            yield a, b


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
