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


def patternize_tails(a, b, s):
    assert len(a) == len(b)
    assert len(a) <= len(s) <= len(a) + 1
    # print('patternize_tails', a, b, s)

    def iter_symbols():
        for aa, bb, ss in zip(a[::-1], b[::-1], s[-len(a):][::-1]):
            yield aa
            yield bb
            yield ss
        if len(s) > len(a):
            yield s[0]

    used = {}
    result = []
    alloc = iter('ABCDEFGHIJ')
    for m in iter_symbols():
        if m not in used:
            used[m] = next(alloc)
        # print(m, used[m], ord(m))
        result.append(used[m])
    return ''.join(result)


def patternize_tails_iterative(a, b, s, include_leading_one=True):
    assert len(a) == len(b)
    assert len(a) <= len(s) <= len(a) + 1

    def iter_symbols():
        for aa, bb, ss in zip(a[::-1], b[::-1], s[-len(a):][::-1]):
            yield (aa, bb, ss)
        if include_leading_one and len(s) > len(a):
            yield (s[0], )

    used = {}
    alloc = iter('ABCDEFGHIJ')
    for triplet in iter_symbols():
        tr = []
        for m in triplet:
            if m not in used:
                used[m] = next(alloc)
            tr.append(used[m])
        yield ''.join(tr)


# print(patternize_tails('удар', 'удар', 'драка'))
# print(list(patternize_tails_iterative('удар', 'удар', 'драка', False)))
