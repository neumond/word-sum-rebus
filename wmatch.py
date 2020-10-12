from utils import patternize_tails_iterative


class DeadPrefixTree:
    __slots__ = ('children', )

    def __init__(self):
        self.children = {}

    def is_dead_end(self):
        return self.children is True

    def is_in_tree(self, a, b, s):
        node = self
        for triplet in patternize_tails_iterative(a, b, s):
            if node.is_dead_end():
                return True
            if triplet not in node.children:
                return False
            node = node.children[triplet]
        assert False

    def add_to_tree(self, tail_pattern):
        assert len(tail_pattern) % 3 == 0
        node = self
        for base in range(0, len(tail_pattern), 3):
            triplet = tail_pattern[base:base + 3]
            if triplet not in node.children:
                node.children[triplet] = DeadPrefixTree()
            node = node.children[triplet]
        node.children = True



# print(attempt2('овец', 'ание', 'ание'))


# print(list(patternize_tails_iterative('аароновец', 'нашивание', 'нагнивание')))


# tree = DeadPrefixTree()
# print(tree.is_in_tree('деталь', 'деталь', 'изделие'))
# tree.add_to_tree(patternize_tails('аль', 'аль', 'лие'))
# print(tree.is_in_tree('деталь', 'деталь', 'изделие'))


class TreeStat:
    def __init__(self):
        self.hit = 0
        self.miss = 0
        self.add = 0

    def __str__(self):
        return f'hit {self.hit}; miss {self.miss}; add {self.add}'


def attempt3(a, b, s, tree, tstat):
    if tree.is_in_tree(a, b, s):
        tstat.hit += 1
        return False, ()
    success, data = attempt2(a, b, s)
    if success:
        tstat.miss += 1
        return True, data
    elif data is not None:
        tstat.add += 1
        tree.add_to_tree(data)
    else:
        tstat.miss += 1
    return False, ()


def run_global_iteration():
    from tqdm import tqdm

    from equations import iterate_pairs, iterate_with_sums, load_word_database

    words = load_word_database()
    # words = ['деталь', 'изделие', 'удар', 'драка']
    # words.sort()
    tree = DeadPrefixTree()
    tstat = TreeStat()
    last_word = None

    from time import time
    with open(f'find_{int(time())}.log', 'w') as f:
        for a, b, s in iterate_with_sums(
            words, iterate_pairs(words),
        ):
            if a != last_word:
                tqdm.write(f'{a} {tstat}')
                f.write(f'{a} {tstat}\n')
                f.flush()
                last_word = a
            success, data = attempt2(a, b, s)
            # success, data = attempt3(a, b, s, tree, tstat)
            # print(a, b, s)
            if success:
                tqdm.write(f'{a} + {b} = {s} {data}')
                f.write(f'{a} + {b} = {s} {data}\n')
                f.flush()
    tqdm.write(str(tstat))


# run_global_iteration()

from equations import iterate_pairs, iterate_with_sums, load_word_database
words = load_word_database()
print(len(words))
print(words[:50])
