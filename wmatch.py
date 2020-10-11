from itertools import permutations
# from equations import attempt_to_match


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


def numpool(chars):
    chars = list(chars)
    print(chars)
    freenums = set(range(10))
    stack = []
    skip_add = False
    while True:
        if not skip_add and len(stack) < len(chars):
            # add new
            n = 0
            while n not in freenums:
                n += 1
            assert n < 10
            stack.append(n)
            yield True, n, chars[len(stack) - 1]
            freenums.remove(n)
            continue

        skip_add = False

        # try to switch current
        for n in range(stack[-1] + 1, 10):
            if n in freenums:

                # switch
                freenums.add(stack[-1])
                yield False, stack[-1], chars[len(stack) - 1]
                stack[-1] = n
                yield True, n, chars[len(stack) - 1]
                freenums.remove(n)

                break
        else:
            # exhausted, pop from stack
            yield False, stack[-1], chars[len(stack) - 1]
            freenums.add(stack.pop(-1))
            if len(stack) == 0:
                return
            skip_add = True


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

    c = 0
    chars2 = list(uniq_char_sequence(char_sequence2(a, b)))
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
        c += 1

        if char_map.left <= 0:
            assert char_map.left == 0
            return collect_result(char_map.char_map, a, b, s)


# print(attempt2('аароновец', 'нашивание', 'нагнивание'))
print(attempt2('деталь', 'деталь', 'изделие'))
