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
import c47sim

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
        out += ['T: ' + row(kt), 'F: ' + row(kf)]
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


def table(f):
    """Key 6 after 5: the truth table (small font): a header ' p q | Φ' over each column of 16, then the rows from
    all true down to all false (the first variable changing slowest), the formula's value last; ' BLOCK 1' ... under
    the columns when there are more than one."""
    shots, texts, c = L.run(L.keys(f) + [L.TABLE, L.EVAL, L.END])
    small = [t for g, t in texts if g == 10]
    i = max(k for k, t in enumerate(small) if t.startswith(' ') and t.rstrip().endswith('| Φ'))
    while i > 0 and small[i - 1].startswith(' ') and '|' in small[i - 1] and small[i - 1] != 'ANY KEY: BACK':
        i -= 1
    end = small.index('ANY KEY: BACK', i)
    blocks = [t for t in small[i:end] if t.startswith(' BLOCK ')]
    got_ = [t for t in small[i:end] if not t.startswith(' BLOCK ')]
    e = parse(f); used = [v for v in VARS if v in f]; n = len(used)
    head = ' ' + ''.join(v + ' ' for v in used) + '| Φ'
    want = []
    for j, k in enumerate(range(2 ** n - 1, -1, -1)):
        if j % 16 == 0:
            want.append(head)
        bits = [k >> (n - 1 - a) & 1 for a in range(n)]
        row = {v: False for v in VARS}; row.update({v: bool(b) for v, b in zip(used, bits)})
        want.append(' ' + ''.join('%d ' % b for b in bits) + '| %d' % e(row))
    check(got_ == want, 'table %s: %s / %s' % (f, got_[:4], want[:4]))
    nb = 2 ** n // 16
    check(sorted(blocks) == ([' BLOCK %d' % b for b in range(1, nb + 1)] if nb > 1 else []), 'table %s: blocks %s' % (f, blocks))


def ascii_only():
    """Every αPOS / αSL / αLEFT of a run works on ASCII texts only (the register and the text searched for): on
    the C47 a glyph such as ¬ may take two bytes, and these commands would then not count it as one character.
    And αSL / αLEFT never go past the end of the text (an error on the C47; c47sim lets it pass): the pages
    1 2 3 shown, F5 F6 on page 3 (no symbol there)."""
    shots, texts, c = None, None, None
    import c47sim
    bad = []
    cls = type(c47sim.load([L.PROG]))

    def hook(self, op, x):
        if op in ('αPOS', 'αSL', 'αLEFT'):
            ln = self.lines[self.at]; reg = ln.split(' ', 1)[1]
            v = self.rget(self.regkey(reg))
            for t in (v, x if op == 'αPOS' else ''):
                if isinstance(t, str) and not t.isascii():
                    bad.append((ln, t))
            if op in ('αSL', 'αLEFT') and isinstance(v, str) and int(x) > len(v):
                bad.append((ln, 'past the end: %s of "%s"' % (int(x), v)))     # an error on the C47
    cls.count = hook
    try:
        for f in ('((p→q)∧(q→r))→(p→r)', '¬(p⊕q)↔(r∨⊤)∧⊥', 'p∧∨q', '(s→t)∧u'):
            L.run(L.keys(f) + [L.DEL] + L.keys(f[-1], True) + [74, 73, 72, 74, 15, 16, L.END])
    finally:
        del cls.count
    check(not bad, 'αPOS / αSL / αLEFT on a non-ASCII text, or past its end: %s' % bad[:3])


def main():
    ascii_only()
    print('the text commands: ASCII only')
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
    for f in ('p', 'p→q', '(p∨q)∧¬r', '¬(p∧q)↔(¬p∨¬q)', 'q⊕s', '(p→q)∧(r↔s)∨(t⊕u)', '⊤∨⊥', 'p∧t∨¬u'):
        table(f)
    print('the truth tables (key 6)')
    # key 6 does nothing before 5, after a change of the formula, or after a syntax error
    for ks, what in ((L.keys('p∧q', False) + [L.TABLE], 'before 5'), (L.keys('p∧q') + L.keys('∨', False) + [L.TABLE], 'after a change'),
                     (L.keys('p∧∨q') + [L.TABLE], 'after a syntax error')):
        shots, texts, c = L.run(ks + [L.END])
        check('ANY KEY: BACK' not in [t for g, t in texts], 'key 6 %s: no table' % what)
    # 4 deletes the last symbol, 7 clears: "p∧q" then 4 4 "∨¬p" -> p∨¬p; 7 then "p∧¬p"
    shots, texts, c = L.run(L.keys('p∧q', False) + [L.DEL, L.DEL] + L.keys('∨¬p'))
    check(got(texts) == expect('p∨¬p'), 'delete: %s' % got(texts))
    shots, texts, c = L.run(L.keys('p∨q', False) + [L.CLEAR] + L.keys('p∧¬p'))
    check(got(texts) == expect('p∧¬p'), 'clear: %s' % got(texts))
    # the stack kept, R20-R98 cleared, GRMOD 0, GRFNT 20 at the end
    shots, texts, c = L.run(L.keys('p→q') + [L.END], stack=(1, 2, 3, 4))
    check([int(v) for v in c.s[:4]] == [1, 2, 3, 4], 'stack: %s' % c.s[:4])
    left = [k for k, v in c.reg.items() if k.isdigit() and 20 <= int(k) <= 98 and v not in (0, '', D(0))]
    check(not left, 'registers left: %s' % left)
    check(getattr(c, 'grmod', 0) == 0 and getattr(c, 'grfnt', 20) == 20, 'GRMOD 0, GRFNT 20 at the end')
    # the standby check: a key wait with no key and the clock 10 min on (the calculator was in standby) ends
    # the program; in the truth table it goes back and the next main pass ends it; 5 s: it waits on
    def standby(ks, gap):
        c = c47sim.load([L.PROG])
        c.s = [D(1), D(2), D(3), D(4)]; c.pix = []; c.frames = []; c.clock = 2461338.0
        script = list(ks)

        def count(op, x):
            if op == 'KEY?':
                k = script.pop(0) if script else L.END
                if k is None:
                    c.keys = []; c.keyskip = True; c.clock += gap / 86400.0
                else:
                    c.keys = [k]; c.keyskip = False
        c.count = count
        c.run('LOGIC47', maxsteps=10 ** 8)
        return c, script
    f = L.keys('p→q')
    c, left = standby(f[:2] + [None] + f[2:] + [L.END], 600)
    check(left == f[2:] + [L.END] and [int(v) for v in c.s[:4]] == [1, 2, 3, 4] and c.pix == [],
          'standby in the main wait: the program ends, the stack back (keys left %s)' % left)
    c, left = standby(f + [L.TABLE, None, None, L.EVAL, L.END], 600)
    check(left == [L.EVAL, L.END] and [int(v) for v in c.s[:4]] == [1, 2, 3, 4] and c.pix == [],
          'standby in the table: back, and the next pass ends the program (keys left %s)' % left)
    c, left = standby(f[:2] + [None] + f[2:] + [L.END], 5)
    check(left == [], 'a gap of 5 s: it waits on (keys left %s)' % left)
    print('ALL OK' if not FAIL else '%d FAILED' % len(FAIL))
    return not FAIL


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
