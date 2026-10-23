# Logic 47: development notes

## Oct 23, 2026 - v0.1.0, the first version

- Idea (Victor): propositional logic on the C47, the verdict only (tautology, contradiction, contingency), not
  the whole table. Variables p q r s t u: six, one row of soft keys, and 2^6 = 64 rows = one 64-bit word.
- The fonts (checked in python/stdfont.py, tinyfont.py from the firmware): ¬ ∧ ∨ ⊕ → ↔ ⊤ ⊥ in the standard font
  (GRFNT 21); ↔ ⇔ missing in the tiny font, ∀ ⊨ ∴ in neither.
- The C47's bitwise commands (docs/reference/C47_Full_index.txt of Almanac 47): AND OR XOR NOT NAND NOR, BS? BC?
  (bit set / clear? a test, with IND), #B. LOGIC47 uses AND OR XOR NOT BS? BC? (no arithmetic on the words:
  mixing reals and short integers left out). Not yet run on a C47: new to these projects.
- Words (WSIZE 64, #2 literals as Elements 47): bit k of variable i = bit i of k; ⊤ 64 ones, ⊥ 0.
- Evaluation: shunting-yard in one pass, the values on R50-R69 (pointer R35), the operators on R70-R89 (R36),
  STO IND / RCL IND. Codes = places in "pqrstu⊤⊥¬∧∨⊕→↔()"; precedence from the digits of 543321 for the codes
  8-13; → right-associative; ¬ pushed at once (prefix). Syntax errors: a value missing (the stack empty: 0
  pushed so the run goes on), ")" without "(", "(" left at the end, not exactly one value at the end.
- The answer: BS? / BC? IND on the 64 bits, from 63 down (the lowest true and false rows last); the variables
  used by αPOS in the formula; true rows / 2^(6 - n).
- Input: soft keys F1-F6 (KEY? 11-16, Elements 47) on three pages (1 2 3), drawn under the screen; 4 delete,
  5 evaluate, 7 clear, 0 end. The formula is ">" then its symbols (one character each).
- c47sim: the bitwise commands added at the end of its run loop (marked logic47). Two slips found there: the
  bit number named n overwrote run()'s step counter (as Date→ⅅ in Zones 47), and IND was resolved twice.
- 693 steps, about 2.7 KB, no IF, 10 DO (the original DM42's limit). A 20-symbol formula about 2 500 steps.
- Tests (tests/test_logic47.py): 39 fixed formulas (laws, precedence without brackets, syntax errors), 317
  random formulas of 1-6 variables, delete and clear, the stack: all against a separate recursive-descent
  evaluator. ALL OK.

## Oct 23, 2026 - v0.1.1: the formula kept in ASCII (Victor: "fails for p and not q" on his C47)

- In the simulator p∧¬q was right (contingency, 1 of 4). The likely cause on the C47: v0.1.0 used αPOS, αSL and
  αLEFT on texts with the glyphs ¬ ∧ ∨ ⊕ → ↔ ⊤ ⊥ (the formula, the symbol table, the pages); in the firmware's
  strings such a glyph may take two bytes, and these commands would then not count it as one character, so the
  codes after the first glyph shift. c47sim counts Python characters and could not show it.
- Now the formula is kept as ASCII letters a-p (the codes 0-15), the pages and the table too; the glyphs are
  only drawn (LBL 74-89: one per code), the formula's glyph text rebuilt in LBL :SHOWF: (a LBL / DSE / GTO
  loop: the program has the original DM42's 10 DO already). Variables' names from "pqrstu" (ASCII).
- tests/test_logic47.py checks that every αPOS / αSL / αLEFT of a run sees ASCII texts only (it fails on
  v0.1.0). All tests OK. 774 steps, about 2.9 KB; R20-R95 cleared at the end.

## To do

1. Run on Victor's C47: the bitwise commands first.
2. Ideas: show the truth table (scroll), equivalence of two formulas, normal forms (DNF / CNF), v w (7-8
   variables: two or four words).
