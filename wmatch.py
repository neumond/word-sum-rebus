from itertools import islice
from time import monotonic

from matching import prefix_match, strict_match
from patterns import patternize_tails_iterative


class DeadPrefixTree:
    max_depth = 10

    def __init__(self):
        self.children = {}  # nested dicts
        self.tree_size = 0
        self.reset_stat()

    def check_and_store(self, a, b, s):
        self.call_count += 1
        current = self.children
        for tail_len, triplet in enumerate(
            islice(
                patternize_tails_iterative(a, b, s, include_leading_one=False),
                self.max_depth,
            ),
            start=1,
        ):
            if triplet not in current:
                m = self.match_fn(a[-tail_len:], b[-tail_len:], s[-tail_len:])
                current[triplet] = {} if m else False
                self.tree_size += 1
            current = current[triplet]
            if current is False:
                self.result_dead_count += 1
                return False
        return True

    def match_fn(self, a, b, s):
        # print('match', a, b, s)
        self.match_call_count += 1
        return prefix_match(a, b, s)

    def reset_stat(self):
        self.call_count = 0
        self.result_dead_count = 0
        self.match_call_count = 0
        self.last_tree_size = self.tree_size
        self.last_time = monotonic()

    def report_str(self):
        dt = monotonic() - self.last_time
        dsize = self.tree_size - self.last_tree_size
        return (
            f'calls:+{self.call_count}'
            f' dead:+{self.result_dead_count}'
            f' matchcalls:+{self.match_call_count}'
            f' treesize:{self.tree_size}(+{dsize})'
            f' time:+{dt:.1f}s'
        )


# tree = DeadPrefixTree()
# print(tree.check_and_store('деталь', 'деталь', 'изделие'))
# print(tree.check_and_store('деталь', 'деталь', 'изделие'))
# print(tree.check_and_store('аароновец', 'нашивание', 'нагнивание'))
# print(tree.check_and_store('аароновец', 'нашивание', 'нагнивание'))
# print(tree.children)
# print(tree.report_str())


def run_global_iteration():
    from time import time

    from tqdm import tqdm

    from sieve import Words

    words = Words.load_full()
    words.a_filter = lambda w: len(w) >= 10
    # words.a_filter = lambda w: w == 'азас'
    # words = Words(['деталь', 'изделие', 'удар', 'драка'])

    tree = DeadPrefixTree()
    last_word = None

    with open(f'find_{int(time())}.log', 'w') as f:
        def write(s):
            tqdm.write(s)
            f.write(s + '\n')
            f.flush()

        for a, b, s in words.iterate_with_sums():
            if a != last_word:
                if last_word is not None:
                    write(f'{last_word} {tree.report_str()}')
                    tree.reset_stat()
                last_word = a
            if not tree.check_and_store(a, b, s):
                continue
            result = strict_match(a, b, s)
            if result is not None:
                write(f'... {a} + {b} = {s} {result}')


run_global_iteration()
