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

## Oct 23, 2026 - v0.1.2: key 3 (Victor: "pushing 3 is giving error" on his C47)

- Key 3 shows page 3, `( ) ⊤ ⊥`: four symbols, but LBL :LABELS: always drew six soft-key labels, and for the
  5th and 6th it ran αSL / αLEFT past the end of the page's text "opgh": an error on the C47. c47sim returned an
  empty text and went on, so the simulator and the tests could not show it.
- Now the loop runs over the page's length (αPOS of a "|" put at its end): six labels on pages 1 and 2, four on
  page 3. F5 / F6 on page 3 already did nothing.
- tests/test_logic47.py: the text check now also fails when αSL / αLEFT go past the end of a text, and presses
  1 2 3 and F5 F6 on page 3 (it fails on v0.1.1). All tests OK. 779 steps, about 2.9 KB.

## Oct 23, 2026 - v0.1.3: true shown as T (Victor: "the T is like superindex")

- The firmware font's ⊤ (stdfont: 9 rows at the top of the 21-row cell, the transpose sign) looks like a
  superscript beside ⊥ (12 rows, on the line). LBL 80 now draws a plain "T" (soft key and formula).

## Oct 23, 2026 - v0.1.4: exclusive or drawn as ⊻ (Victor: "the circle with plus is low in the bar")

- The firmware font's ⊕ (stdfont: rows 10-20 of the cell, nothing below) sits lower than ∧ ∨ (rows 7-15) on the
  soft keys and in the formula. LBL 85 now draws ⊻ (rows 7-19, as ∨ with a bar under it), the other usual sign
  for exclusive or. The simulator and the tests still name it ⊕ when they type a formula.

## Oct 23, 2026 - v0.1.5: the user's stack saved with STOS / RCLS

- From the forum: LocR 9, STOS R.00 (the stack in R.00-R.07), LASTx in R.08; at the end RCL R.08, STO L,
  RCLS R.00, in place of STO R.00 R↓ ... (8 times) and RCL R.07 ... R.00. Victor ran STOS / RCLS on his C47
  (Oct 23): the stack and LASTx came back.
- c47sim: STOS / RCLS copied from Almanac 47 (branch c47sim-stos-rcls). All tests OK. 757 steps (22 fewer).

## To do

1. Run on Victor's C47: the bitwise commands first.
2. Ideas: show the truth table (scroll), equivalence of two formulas, normal forms (DNF / CNF), v w (7-8
   variables: two or four words).
