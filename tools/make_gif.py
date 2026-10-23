#!/usr/bin/env python3
"""Write docs/LOGIC47_demo.gif: LOGIC47 in the C47 simulator, two formulas typed with the soft keys and
evaluated (a tautology, a contingency), 7 clearing between them. Needs Pillow (pip install pillow).
  python3 tools/build_logic47.py && python3 tools/make_gif.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
import logic47sim as L
from PIL import Image

S, B = 2, 8
FORMULAS = ('((p→q)∧(q→r))→(p→r)', '(p∨q)∧¬r')


def image(pix):
    im = Image.new('P', (L.W * S + 2 * B, L.H * S + 2 * B), 0)
    im.putpalette(list(L.LCD_BG) + list(L.LCD_ON) + [0] * 762); px = im.load()
    for x, r in pix:
        for dy in range(S):
            for dx in range(S):
                px[B + x * S + dx, B + r * S + dy] = 1
    return im


def main():
    ks = []
    for f in FORMULAS:
        ks += L.keys(f) + [L.CLEAR]
    shots, texts, c = L.run(ks + [L.END])
    ims = [image(s) for s in shots]
    dur = [2200 if k == L.EVAL else 350 for k in [None] + ks][:len(ims)]
    fn = os.path.join(ROOT, 'docs', 'LOGIC47_demo.gif')
    ims[0].save(fn, save_all=True, append_images=ims[1:], duration=dur, loop=0, optimize=True)
    print('%s: %d frames' % (os.path.relpath(fn, ROOT), len(ims)))


if __name__ == '__main__':
    main()
