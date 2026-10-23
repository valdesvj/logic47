"""logic47sim.py - run build/LOGIC47.txt in the C47 simulator (c47sim.py, from Almanac 47, with the bitwise
commands added for Logic 47) and turn its screens into pictures.
  keys(formula)       the keys that type a formula (soft keys F1-F6 = codes 11-16 on pages 1 2 3) and 5
  run(keys)           the screens shown while LOGIC47 waits for a key, and the texts drawn
  png(fn, pix)        a PNG of one screen (LCD colours, 3 pixels per C47 pixel)
  python3 python/logic47sim.py   writes the screens in docs/"""
import os, struct, sys, zlib
from decimal import Decimal as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import c47sim

PROG = os.environ.get('LOGIC47_PROG') or os.path.join(ROOT, 'build', 'LOGIC47.txt')
W, H = 400, 240
LCD_BG, LCD_ON = (199, 205, 186), (34, 38, 30)
PAGES = ('pqrstu', '¬∧∨→↔⊕', '()⊤⊥')
PAGEKEY = (72, 73, 74)                                    # the keys 1 2 3
DEL, EVAL, CLEAR, END = 62, 63, 52, 82                    # 4 5 7 0


def keys(formula, evaluate=True):
    """The keys that type the formula (each symbol: its page key when the page changes, then its soft key)."""
    out, page = [], 0
    for ch in formula:
        if ch == ' ':
            continue
        p = next(i for i, pg in enumerate(PAGES) if ch in pg)
        if p != page:
            out.append(PAGEKEY[p]); page = p
        out.append(11 + PAGES[p].index(ch))
    return out + ([EVAL] if evaluate else [])


def run(ks, prog=PROG, stack=None):
    c = c47sim.load([prog])
    c.s = [D(v) for v in (stack or (0, 0, 0, 0))]; c.pix = []; c.keys = list(ks); c.steps = 0
    c.frames = []; c.at_steps = []
    texts = []
    cls = type(c); orig = cls.atext

    def hook(self, t):
        texts.append((getattr(self, 'grfnt', 20), str(t))); return orig(self, t)

    class F(list):
        def append(self, f): c.at_steps.append(c.steps); super().append(f)
    c.frames = F()
    cls.atext = hook
    try:
        c.run('LOGIC47', maxsteps=10 ** 7)
    except StopIteration:
        pass
    finally:
        cls.atext = orig
    shots = [{(x, H - 1 - y) for y, x in f if 0 <= y < H and 0 <= x < W} for f in c.frames]
    return shots, texts, c


def png(fn, pix, scale=3, border=12):
    w, h = W * scale + 2 * border, H * scale + 2 * border
    buf = bytearray(bytes(LCD_BG) * (w * h))
    dot = bytes(LCD_ON) * scale
    for x, r in pix:
        for dy in range(scale):
            o = ((border + r * scale + dy) * w + border + x * scale) * 3
            buf[o:o + len(dot)] = dot
    raw = b''.join(b'\x00' + bytes(buf[y * w * 3:(y + 1) * w * 3]) for y in range(h))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(fn, 'wb') as fh:
        fh.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                 + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


SHOTS = [('LOGIC47_tautology.png', '((p→q)∧(q→r))→(p→r)'), ('LOGIC47_contingency.png', '(p∨q)∧¬r'),
         ('LOGIC47_contradiction.png', 'p∧¬p'), ('LOGIC47_syntax.png', 'p∧∨q')]


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
    for fn, f in SHOTS:
        shots, texts, c = run(keys(f) + [END])
        png(os.path.join(ROOT, 'docs', fn), shots[-1])
        print('docs/%-26s %-24s %s  (evaluation %d steps)' % (fn, f, [t for g, t in texts if g == 21][-3:],
                                                           c.at_steps[-1] - c.at_steps[-2]))
