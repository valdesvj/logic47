#!/usr/bin/env python3
"""build_forum.py - the commented rejig source (.p47u) of LOGIC47, for the forum and the PROGRAMS folder of a C47
release (as Almanac 47's and Zones 47's tools/build_forum.py: '@' header lines, then the steps).

  build/forum/LOGIC47.p47u  from build/LOGIC47.txt (the steps) and listings/LOGIC47_doc.txt (the comments)

The steps are those of build/*.txt, one by one (the same .p47 as the plain listing): indented as the source
(STRUCT, two spaces a level), the partner numbers written (DO 01 ... ENDDO 01). The comments of the source
(its REM lines) go after ';' at the end of the steps they stand before, one comment line a step, in a column;
the name of a label (LBL :INIT:) is given as a comment on its LBL and on each XEQ / GTO to it. rejig drops
everything after ';', so the comments take no memory. A line that starts with ';' or '#' would become a REM
step on the calculator (Almanac 47 DEVELOPMENT_NOTES): there are none; the source's header is in '@' lines.

  python3 tools/build_logic47.py   (writes it too)
  rejig: the .p47 of build/forum/LOGIC47.p47u must be the size of the one of build/LOGIC47.txt.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build', 'forum')
AUTHOR = 'Victor Valdes'
SOURCE = 'https://github.com/valdesvj/logic47'
COL = 32                              # the column of the ';' comments (wider steps: two spaces after them)

HEAD = {
    'LOGIC47': """@ Index:   Propositional logic: tautology, contradiction or contingency, and the truth table
@ Author:  %(author)s
@ Version: %(version)s
@ Source:  %(source)s
@ Tested:  on the C47 by the author (Oct 2026)
@ Tested:  C47 simulator (python/c47sim.py): tests/test_logic47.py, 39 fixed formulas and 317 random ones of
@ Tested:  1-6 variables against a separate Python evaluator
@ Input:   the formula, keyed with F1-F6 on three pages (1 p q r s t u, 2 the connectives, 3 ( ) T F)
@ Output:  p->q (keys F1, 2 F4, 1 F2, 5): CONTINGENCY, true in 3 of 4 rows, T: p=0 q=0, F: p=1 q=0;
@ Output:  then 6: the table p q | f: 1 1 | 1, 1 0 | 0, 0 1 | 1, 0 0 | 1
@
@ Logic 47: propositional logic on the C47 / R47. Variables p q r s t u, the constants true and false,
@ not, and, or, exclusive or, implies, if and only if, brackets. 5 evaluates the formula: TAUTOLOGY,
@ CONTRADICTION or CONTINGENCY, the number of true rows, and for a contingency a true and a false row.
@ Each variable is a 64-bit word (one bit a row), so the formula is evaluated once with AND OR XOR NOT.
@
@ Keys: F1-F6 a symbol, 1 2 3 the page, 4 delete, 5 evaluate, 6 the truth table (after 5; up to 64 rows on one
@ screen, any key back), 7 clear, 0 the end.
@ Your stack and LASTx are kept (STOS / RCLS in local registers); the registers R20-R96 are cleared at the end.
@ Needs a C47 / R47 firmware with ATEXT, GRFNT, the STRUCT commands and the bitwise commands (WSIZE 64).
@ The comments after ';' say what each part does (rejig drops them: they take no memory).
@
""",
}

STEP = re.compile(r'^\s*(\d+)  (.*)$')
NAMED = re.compile(r'^(\s*)(.*?)\s{4}\((\d+)\)$')            # "XEQ :INIT:    (83)", "DO    (01)"


def parse(name):
    """The doc listing: the header comments, then [(indent, step text with names, number, comments before it)]."""
    head, steps, pending = [], [], []
    for ln in open(os.path.join(ROOT, 'listings', name + '_doc.txt'), encoding='utf-8'):
        ln = ln.rstrip('\n')
        m = STEP.match(ln)
        if m:
            body = m.group(2)
            ind = body[:len(body) - len(body.lstrip())]
            steps.append((ind, body.strip(), int(m.group(1)), pending)); pending = []
        elif ln.strip().startswith(';'):
            text = ln.strip()[1:].strip()
            (pending if steps else head).append(text)          # before step 1: the program's header
    return head, steps


def data_notes(name, plain, names):
    """Notes on the tables (no REM of their own): {step index: note}. LBL 60 + code: the connectives (XEQ IND,
    the codes 8-13), LBL 74 + code: the glyph of each code 0-15 (as drawn)."""
    sym = ['p', 'q', 'r', 's', 't', 'u', 'true (drawn T)', 'false', 'not', 'and', 'or', 'exclusive or (drawn ⊻)',
           'implies', 'if and only if', '(', ')']
    notes = {}
    for k, st in enumerate(plain):
        m = re.fullmatch(r'LBL (\d\d)', st)
        if m and m.group(1) not in names:
            lab = int(m.group(1))
            if 68 <= lab <= 73:
                notes[k] = 'connective code %d (%s): pops its operands, pushes the result word' % (lab - 60, sym[lab - 60])
            elif 74 <= lab <= 89:
                notes[k] = 'glyph of code %d (letter %s): %s' % (lab - 74, chr(97 + lab - 74), sym[lab - 74])
    return notes


def build(name):
    head, steps = parse(name)
    plain = open(os.path.join(ROOT, 'build', name + '.txt'), encoding='utf-8').read().split('\n')
    plain = [s for s in plain if s.strip()]
    if len(plain) != len(steps):
        raise SystemExit('%s: %d steps in build/, %d in listings/' % (name, len(plain), len(steps)))
    m = re.search(r'v(\d+\.\d+\.\d+)', head[0])
    version = m.group(1) if m else '?'
    names = {}                                                    # label number -> :NAME:
    for ind, text, n, com in steps:
        mm = NAMED.match(ind + text)
        if mm and mm.group(2).startswith('LBL :'):
            names[mm.group(3)] = mm.group(2)[4:]
    out = [(HEAD[name] % dict(author=AUTHOR, version=version, source=SOURCE)).rstrip('\n')]
    data = data_notes(name, plain, names)
    out += ['@ ' + h if h else '@' for h in head] + ['@', '']
    queue, last = [], None
    for k, ((ind, text, n, com), step) in enumerate(zip(steps, plain)):
        if ';' in step or step.lstrip().startswith(('#', '@')):
            raise SystemExit('%s step %d: %r would not survive rejig' % (name, n, step))
        if com:
            if queue and last is not None:                       # the rest of the last block: on its last step
                out[last] += ' ' + ' '.join(queue)
            queue = list(com)
        note = ''
        mm = re.fullmatch(r'(LBL|XEQ|GTO) (\d\d)', step)
        if mm and mm.group(2) in names:
            note = names[mm.group(2)] if mm.group(1) == 'LBL' else '-> ' + names[mm.group(2)]
        if k in data:
            note = (note + '  ' if note else '') + data[k]
        c = queue.pop(0) if queue else ''
        if note and c:
            c = note + '  ' + c
        elif note:
            c = note
        line = ind + step
        if c:
            line = line.ljust(COL) + '; ' + c if len(line) < COL else line + '  ; ' + c
        out.append(line)
        if c:
            last = len(out) - 1
    if queue and last is not None:
        out[last] += ' ' + ' '.join(queue)
    os.makedirs(OUT, exist_ok=True)
    fn = os.path.join(OUT, name + '.p47u')
    with open(fn, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out).rstrip('\n') + '\n')
    ncom = sum(1 for ln in out if re.search(r'\s; ', ln))
    print('build/forum/%s.p47u  %d steps, %d with a comment, version %s' % (name, len(plain), ncom, version))
    return out


if __name__ == '__main__':
    for nm in sys.argv[1:] or ('LOGIC47',):
        build(nm)
