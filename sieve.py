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


class Words:
    def __init__(self, words):
        self.words = words
        self.mask_index_by_len = {
            wlen: LetterMaskIndex(wlist)
            for wlen, wlist in split_by_length(words).items()
        }

    @classmethod
    def load_full(cls):
        import gzip

        words = []
        with gzip.open('words.txt.gz', 'rt', encoding='utf-8') as f:
            for line in f:
                words.append(line.strip())
        return cls(words)

    def a_filter(self, a):
        return True

    def pair_filter(self, a, b):
        return True

    def iterate_pairs(self):
        # 85297031 pairs

        alist = [w for w in self.words if self.a_filter(w)]
        for a in tqdm(alist):
            for b in self.mask_index_by_len[len(a)].search_submatches(a):
                if a > b:
                    continue
                if not self.pair_filter(a, b):
                    continue
                yield a, b

    def iterate_with_sums(self):
        for a, b in self.iterate_pairs():
            mi = self.mask_index_by_len[len(a)]
            for s in mi.search_submatches(a + b):
                yield a, b, s
            if (len(a) + 1) in self.mask_index_by_len:
                mi = self.mask_index_by_len[len(a) + 1]
                for s in mi.search_submatches(a + b):
                    yield a, b, s
