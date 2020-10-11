from equations import patternize_tails, patternize_tails_iterative

MULTIPLIERS = [10 ** i for i in range(20)]


def char_sequence2(a, b):
    for ac, bc in zip(a[::-1], b[::-1]):
        yield ac
        yield bc


def char_sequence3(a, b, s):
    for ac, bc, sc in zip(a[::-1], b[::-1], s[::-1]):
        yield ac
        yield bc
        yield sc
    if len(s) > len(a):
        yield s[0]


def uniq_char_sequence(seq, prefill=()):
    k = set(prefill)
    for ch in seq:
        if ch not in k:
            yield ch
            k.add(ch)


def numpool2(chars, freenums, pos=0):
    for i in range(10):
        if i not in freenums:
            continue
        accept = yield True, i, pos
        if not accept:
            continue
        freenums.remove(i)
        if pos + 1 < len(chars):
            yield from numpool2(chars, freenums, pos + 1)
        yield False, i, pos
        freenums.add(i)


class Column:
    def __init__(self, a, b, s):
        self.a, self.b, self.s = a, b, s
        self.an, self.bn = None, None
        self.carry = None
        self.next_col = None

    def get_sym_detect(self):
        return set([self.a, self.b])

    def _set_symbol(self, sym, n):
        if sym == self.a:
            self.an = n
        if sym == self.b:
            self.bn = n

    def is_filled(self):
        return (
            self.an is not None
            and self.bn is not None
            and self.carry is not None
        )

    def _get_sum_range(self):
        min_sum = 0
        max_sum = 0
        for n in self.an, self.bn:
            if n is not None:
                min_sum += n
                max_sum += n
            else:
                max_sum += 9
        if self.carry is None:
            max_sum += 1
        else:
            min_sum += self.carry
            max_sum += self.carry
        return min_sum, max_sum

    def _get_carry_for_next_column(self):
        min_sum, max_sum = self._get_sum_range()
        if min_sum >= 10:
            return 1
        if max_sum < 10:
            return 0
        return None

    def _propagate_carry(self):
        if self.next_col is None:
            return
        next_carry = self._get_carry_for_next_column()
        if self.next_col.carry == next_carry:
            return
        self.next_col.carry = next_carry
        return self.next_col._propagate_carry()

    def set_symbol(self, sym, n):
        self._set_symbol(sym, n)
        self._propagate_carry()

    def __str__(self):
        return f'{self.an}+{self.bn}+{self.carry}'


class ColumnSet:
    def __init__(self, a, b, s):
        self.columns = []
        for ac, bc, sc in zip(a, b, s[-len(a):]):
            self.columns.append(Column(ac, bc, sc))

        self.columns[-1].carry = 0
        for next_col, prev_col in zip(self.columns, self.columns[1:]):
            prev_col.next_col = next_col

        self.sym_col_map = {}
        for col in reversed(self.columns):
            for sym in col.get_sym_detect():
                self.sym_col_map.setdefault(sym, []).append(col)

    def set_symbol(self, sym, n):
        min_col = None
        for col in self.sym_col_map[sym]:
            col.set_symbol(sym, n)
            if min_col is None:
                min_col = col
        return min_col

    def debug(self):
        def pn(n):
            if n is None:
                return '.'
            return str(n)

        a = ''.join(pn(col.an) for col in self.columns)
        b = ''.join(pn(col.bn) for col in self.columns)
        return f'{a} + {b}'


def collect_update_from_column_chain(col):
    while col is not None:
        if col.is_filled():
            yield col.s, col._get_sum_range()[0] % 10
        col = col.next_col


class StackConflictError(Exception):
    pass


class CharmapStack:
    def __init__(self, all_symbols):
        self.char_map = {}
        self.reverse_map = {}
        self.left = len(set(all_symbols))
        self.history = []

    def set_checkpoint(self):
        # print('checkpoint', len(self.history))
        self.history.append((
            self.char_map.copy(),
            self.reverse_map.copy(),
            self.left,
        ))

    def revert_to_checkpoint(self):
        self.char_map, self.reverse_map, self.left = self.history.pop(-1)
        # print('revert', len(self.history))

    def set_item(self, sym, n):
        assert n is not None
        if sym not in self.char_map:
            if n in self.reverse_map:
                # print('char conflict (reverse)', sym, self.reverse_map[n], n)
                raise StackConflictError
            # print('set symbol', sym, n)
            self.char_map[sym] = n
            self.reverse_map[n] = sym
            self.left -= 1
        elif self.char_map[sym] != n:
            # print('char conflict', sym, self.char_map[sym], n)
            raise StackConflictError


def collect_result(char_map, a, b, s):
    at = int(''.join(str(char_map[ch]) for ch in a))
    bt = int(''.join(str(char_map[ch]) for ch in b))
    st = int(''.join(str(char_map[ch]) for ch in s))
    assert at + bt == st
    return at, bt


def attempt2(a, b, s):
    cs = ColumnSet(a, b, s)
    char_map = CharmapStack(a + b + s)

    if len(s) > len(a):
        char_map.set_item(s[0], 1)

    chars2 = list(uniq_char_sequence(char_sequence2(a, b)))
    # possible improvement:
    # remove/restore items in arguments of numpool2
    ng = numpool2(chars2, set(range(10)))
    max_depth = 0
    decision = None
    while True:
        try:
            op, n, chpos = ng.send(decision)
        except StopIteration:
            break
        decision = True
        ch = chars2[chpos]
        max_depth = max(max_depth, chpos)
        if op:
            char_map.set_checkpoint()
            try:
                char_map.set_item(ch, n)
                col = cs.set_symbol(ch, n)
                for setsym, setn in collect_update_from_column_chain(col):
                    char_map.set_item(setsym, setn)
            except StackConflictError:
                cs.set_symbol(ch, None)
                char_map.revert_to_checkpoint()
                decision = False
        else:
            cs.set_symbol(ch, None)
            char_map.revert_to_checkpoint()
        # print(cs.debug())

        if char_map.left <= 0:
            assert char_map.left == 0
            try:
                return True, collect_result(char_map.char_map, a, b, s)
            except AssertionError:
                pass

    if max_depth >= len(a) - 1:
        return False, None
    return False, patternize_tails(
        a[-max_depth:], b[-max_depth:], s[-max_depth:])


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


# print(attempt2('аароновец', 'нашивание', 'нагнивание'))
# print(attempt2('деталь', 'деталь', 'изделие'))
# print(attempt2('удар', 'удар', 'драка'))
# print(attempt2('трюк', 'трюк', 'цирк'))
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
