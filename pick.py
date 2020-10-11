a = 'аароновец'
b = 'авиамотор'


def patternize(word):
    used = {}
    result = []
    alloc = iter('ABCDEFGHIJ')
    for s in word:
        if s not in used:
            used[s] = next(alloc)
        result.append(used[s])
    return ''.join(result)


# print(patternize(a + b))


# from itertools import combinations, islice
#
#
# alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
# assert len(alphabet) == 33
# n = 0
# for x in combinations(alphabet, 10):
#     n += 1
# print(n)
# # 92561040


# 1 symbol
# 10 * 10 = 100 possible equations
# some of them are unique
#
#
# 2 symbols
# 100 * 100 = 10000 possible equations
# some of them are unique


def patternize_eq(a, b, s1=False):
    assert a > 0
    assert b > 0

    s = a + b
    if s1:
        s += 1
    a, b, s = map(str, [a, b, s])

    assert len(a) == len(b)
    one = False
    if len(s) > len(a):
        assert len(s) - 1 == len(a)
        assert s[0] == '1'
        # one = True
        s = s[1:]
        assert len(s) == len(a)

    # reverse all strings
    a, b, s = map(lambda x: x[::-1], [a, b, s])

    used = {}
    alloc = iter('ABCDEFGHIJ')

    def convsym(s):
        if s not in used:
            used[s] = next(alloc)
        return used[s]

    ap, bp, sp = '', '', ''
    pfx = ''
    for ax, bx, sx in zip(a, b, s):
        ax = convsym(ax)
        bx = convsym(bx)
        sx = convsym(sx)
        ap = ax + ap
        bp = bx + bp
        sp = sx + sp
        pfx += ax + bx + sx
    if one:
        sp = convsym('1') + sp

    # {ap}+{bp}={sp}
    return pfx


def find_unique_sums(n_syms):
    assert n_syms > 0
    lower = 10 ** (n_syms - 1)
    upper = 10 ** n_syms

    pc = {}
    pex = {}
    n = 0
    for a in range(lower, upper):
        for b in range(a, upper):
            n += 1
            pat = patternize_eq(a, b, s1=True)
            pc.setdefault(pat, 0)
            pc[pat] += 1
            pex[pat] = f'{a}+{b}={a+b+1}'
            # print(f'{a}+{b}={a+b+1}', pat)
    # print(pc)
    # print(n)

    return sorted([(pat, pex[pat]) for pat, n in pc.items() if n == 1])


# us1 = find_unique_sums(1)
# us2 = find_unique_sums(2)
# us3 = find_unique_sums(3)
# us4 = find_unique_sums(4)

# print(us1)
# print(us2)
# print(us3)

# print(len(us1))
# print(len(us2))
# print(len(us3))
# print(us4[:100])


def swap_pattern(p):
    return ''.join(
        f'{b}{a}{s}'
        for a, b, s in zip(p[::3], p[1::3], p[2::3])
    )


def iter_patterns(max_n, prefix=''):
    if max_n < 1:
        return
    letters = 'ABCDEFGHIJ'
    # a + b = c; [a, b, c]
    max_letters = [
        min(tidx + len(prefix) + 1, len(letters))
        for tidx in range(3)
    ]
    for l1 in range(max_letters[0]):
        for l2 in range(max_letters[1]):
            for l3 in range(max_letters[2]):
                val = f'{prefix}{letters[l1]}{letters[l2]}{letters[l3]}'
                sw_val = swap_pattern(val)
                if sw_val >= val:
                    yield val
                    yield from iter_patterns(max_n - 1, val)


from itertools import islice


print(list(iter_patterns(2)))
print(len(list(iter_patterns(3))))
print(
    list(islice(iter_patterns(4), 200))
)
