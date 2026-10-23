#!/usr/bin/env python3
"""tests/test_logic47.py - LOGIC47 in the C47 simulator against a Python evaluator written separately (a
recursive-descent parser with the same precedence: ¬, ∧, ∨ and ⊕, →, ↔; → to the right): the verdict, the true
rows and the example rows of every formula; the precedence and associativity cases written without brackets;
syntax errors; random formulas of 1-6 variables; the keys 4 (delete) and 7 (clear); the user's stack kept.
  python3 tools/build_logic47.py && python3 tests/test_logic47.py"""
import itertools, os, random, sys
from decimal import Decimal as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
import logic47sim as L

VARS = 'pqrstu'
FAIL = []


def check(ok, what):
    if not ok:
        FAIL.append(what); print('FAIL', what)


class Bad(Exception):
    pass


def parse(f):
    """The formula as a Python function of the row (a dict), by recursive descent; Bad on a syntax error."""
    toks = [c for c in f if c != ' ']; pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1; return toks[pos[0] - 1]

    def atom():
        c = peek()
        if c is None:
            raise Bad
        if c == '¬':
            take(); a = atom(); return lambda v: not a(v)
        if c == '(':
            take(); e = iff()
            if take_if(')'):
                return e
            raise Bad
        if c in VARS:
            take(); return lambda v, c=c: v[c]
        if c in '⊤⊥':
            take(); return (lambda v: True) if c == '⊤' else (lambda v: False)
        raise Bad

    def take_if(c):
        if peek() == c:
            take(); return True
        return False

    def conj():
        a = atom()
        while take_if('∧'):
            b = atom(); a = (lambda a, b: lambda v: a(v) and b(v))(a, b)
        return a

    def disj():                                  # ∨ and ⊕: the same level, to the left
        a = conj()
        while peek() in ('∨', '⊕'):
            op = take(); b = conj()
            a = (lambda a, b: lambda v: a(v) or b(v))(a, b) if op == '∨' else \
                (lambda a, b: lambda v: a(v) != b(v))(a, b)
        return a

    def imp():                                   # → to the right
        a = disj()
        if take_if('→'):
            b = imp(); return lambda v: (not a(v)) or b(v)
        return a

    def iff():                                   # ↔ to the left
        a = imp()
        while take_if('↔'):
            b = imp(); a = (lambda a, b: lambda v: a(v) == b(v))(a, b)
        return a

    e = iff()
    if pos[0] != len(toks):
        raise Bad
    return e


def expect(f):
    """The texts LOGIC47 should show: the verdict, the rows, the example (or SYNTAX ERROR)."""
    try:
        e = parse(f)
    except Bad:
        return ['SYNTAX ERROR']
    used = [c for c in VARS if c in f]
    rows = [dict(zip(VARS, (bool(k >> i & 1) for i in range(6)))) for k in range(64)]
    vals = [e(v) for v in rows]
    true = sum(vals) // 2 ** (6 - len(used))
    verdict = 'TAUTOLOGY' if all(vals) else 'CONTRADICTION' if not any(vals) else 'CONTINGENCY'
    out = [verdict, 'true in %d of %d rows' % (true, 2 ** len(used))]
    if verdict == 'CONTINGENCY':
        kt, kf = vals.index(True), vals.index(False)
        row = lambda k: ''.join('%s=%d ' % (c, k >> VARS.index(c) & 1) for c in used)
        out.append('T: ' + row(kt) + '  F: ' + row(kf))
    return out


def got(texts):
    big = [t for g, t in texts if g == 21 and t.strip()]
    if big and big[-1] == 'SYNTAX ERROR':
        return ['SYNTAX ERROR']
    i = max(i for i, t in enumerate(big) if t in ('TAUTOLOGY', 'CONTRADICTION', 'CONTINGENCY'))
    return big[i:]


def one(f):
    shots, texts, c = L.run(L.keys(f) + [L.END])
    check(got(texts) == expect(f), '%s: %s / %s' % (f, got(texts), expect(f)))
    return c


def rand_formula(rng, depth, vs):
    if depth == 0 or rng.random() < 0.25:
        return rng.choice(vs + ['⊤', '⊥'] if rng.random() < 0.05 else vs)
    if rng.random() < 0.2:
        return '¬' + rand_formula(rng, depth - 1, vs)
    op = rng.choice('∧∨⊕→↔')
    a, b = rand_formula(rng, depth - 1, vs), rand_formula(rng, depth - 1, vs)
    wrap = lambda s: '(' + s + ')' if len(s) > 1 and rng.random() < 0.7 else s
    return wrap(a) + op + wrap(b)


def main():
    cases = [
        # the classics
        'p∨¬p', 'p∧¬p', 'p→p', '((p→q)∧p)→q', '((p→q)∧¬q)→¬p', '((p→q)∧(q→r))→(p→r)',
        '¬(p∧q)↔(¬p∨¬q)', '¬(p∨q)↔(¬p∧¬q)', '(p→q)↔(¬q→¬p)', 'p⊕q↔¬(p↔q)', '(p∨q)∧¬r', 'p→q',
        # precedence and associativity without brackets
        'p∨q∧r', 'p∧q∨r', '¬p∧q', '¬¬p', 'p→q→r', 'p↔q↔r', 'p⊕q∨r', 'p∨q⊕r', 'p→q∨r', 'p↔q→r',
        'p∧q→r↔s', '⊤', '⊥', '¬⊤∨p', 'p∧q∧r∧s∧t∧u', 'p∨q∨r∨s∨t∨u', '(((p)))',
        # syntax errors
        'p∧∨q', 'p∧', '∧p', '(p∧q', 'p∧q)', 'pq', '()', '¬', 'p(q)', ')p(',
    ]
    for f in cases:
        one(f)
    print('%d fixed cases' % len(cases))
    rng = random.Random(47)
    n = 0
    for k in range(320):
        vs = list(VARS[:rng.randint(1, 6)])
        f = rand_formula(rng, rng.randint(1, 4), vs)
        if len(f) > 40:
            continue
        one(f); n += 1
    print('%d random formulas' % n)
    # 4 deletes the last symbol, 7 clears: "p∧q" then 4 4 "∨¬p" -> p∨¬p; 7 then "p∧¬p"
    shots, texts, c = L.run(L.keys('p∧q', False) + [L.DEL, L.DEL] + L.keys('∨¬p'))
    check(got(texts) == expect('p∨¬p'), 'delete: %s' % got(texts))
    shots, texts, c = L.run(L.keys('p∨q', False) + [L.CLEAR] + L.keys('p∧¬p'))
    check(got(texts) == expect('p∧¬p'), 'clear: %s' % got(texts))
    # the stack kept, R20-R92 cleared, GRMOD 0, GRFNT 20 at the end
    shots, texts, c = L.run(L.keys('p→q') + [L.END], stack=(1, 2, 3, 4))
    check([int(v) for v in c.s[:4]] == [1, 2, 3, 4], 'stack: %s' % c.s[:4])
    left = [k for k, v in c.reg.items() if k.isdigit() and 20 <= int(k) <= 92 and v not in (0, '', D(0))]
    check(not left, 'registers left: %s' % left)
    check(getattr(c, 'grmod', 0) == 0 and getattr(c, 'grfnt', 20) == 20, 'GRMOD 0, GRFNT 20 at the end')
    print('ALL OK' if not FAIL else '%d FAILED' % len(FAIL))
    return not FAIL


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
