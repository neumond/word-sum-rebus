from itertools import permutations

from patterns import char_sequence2, uniq_char_sequence
from utils import letterset


def bruteforce(a, b, s):
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


def collect_result(char_map, a, b, s, imaginary_one, allow_leading_zero):
    at = ''.join(str(char_map[ch]) for ch in a)
    bt = ''.join(str(char_map[ch]) for ch in b)
    if not allow_leading_zero:
        assert not at.startswith('0')
        assert not bt.startswith('0')
    at, bt = int(at), int(bt)
    st = ''.join(str(char_map[ch]) for ch in s)
    if not imaginary_one:
        assert at + bt == int(st)
    else:
        assert (at + bt == int(st)) or (at + bt == int('1' + st))
    return at, bt


def match(a, b, s, imaginary_one=False, allow_leading_zero=False):
    # print(a, b, s)
    cs = ColumnSet(a, b, s)
    char_map = CharmapStack(a + b + s)

    if len(s) > len(a):
        char_map.set_item(s[0], 1)

    chars2 = list(uniq_char_sequence(char_sequence2(a, b)))
    # possible improvement:
    # remove/restore items in arguments of numpool2
    ng = numpool2(chars2, set(range(10)))
    decision = None
    while True:
        try:
            op, n, chpos = ng.send(decision)
        except StopIteration:
            break
        decision = True
        ch = chars2[chpos]
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
                res = collect_result(
                    char_map.char_map, a, b, s,
                    imaginary_one, allow_leading_zero)
                # print(res)
                return res
            except AssertionError:
                pass

    return None


# print(match('aa', 'bb', 'cc'))
# print(match('аароновец', 'нашивание', 'нагнивание'))
# print(match('деталь', 'деталь', 'изделие'))
# print(match('удар', 'удар', 'драка'))
# print(match('трюк', 'трюк', 'цирк'))


KNOWN_MATCHES = [
    ('деталь', 'деталь', 'изделие'),
    ('удар', 'удар', 'драка'),
    ('трюк', 'трюк', 'цирк'),
    ('абитуриент', 'антиракета', 'бригантина'),
    ('аароновец', 'нашивание', 'нагнивание'),
]


def test_match():
    for a, b, s in KNOWN_MATCHES:
        print(a, b, s, match(a, b, s))
        if len(s) > len(a):
            s = s[1:]
        while len(a) > 0:
            print(a, b, s, match(a, b, s, True, True))
            a, b, s = a[1:], b[1:], s[1:]


test_match()
# print(match('удар', 'удар', 'рака', True, allow_leading_zero=True))
