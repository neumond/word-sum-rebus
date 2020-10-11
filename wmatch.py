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
            self.a is not None
            and self.b is not None
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
        col = min_col
        while col is not None:
            if col.is_filled():
                yield col.s, col._get_sum_range()[0]
            col = col.next_col


def attempt2(a, b, s):
    cs = ColumnSet(a, b, s)

    char_map = {}
    c = 0
    for op, n, ch in numpool(uniq_char_sequence(char_sequence2(a, b))):
        if op:
            assert ch not in char_map
            char_map[ch] = n
            cs.set_symbol(ch, n)
        else:
            assert char_map[ch] == n
            del char_map[ch]
            cs.set_symbol(ch, None)
        c += 1
    return c


# print(attempt2('аароновец', 'нашивание', 'нагнивание'))
print(attempt2('деталь', 'деталь', 'изделие'))
