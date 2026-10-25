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

## Oct 24, 2026 - the commented rejig source build/forum/LOGIC47.p47u (Victor)

- As Zones 47's build/forum: an '@' header, the steps of build/LOGIC47.txt indented (STRUCT), the source's REM lines
  after ';' on the steps they stand before, label names on LBL / XEQ (-> :INIT:), notes on the tables (the
  connectives LBL 68-73, the glyphs LBL 74-89). rejig drops what follows ';': the .p47 is that of build/LOGIC47.txt.
  tools/build_forum.py, run at the end of tools/build_logic47.py; tests/test_forum.py. The source's header now
  says v0.1.5 and the glyphs drawn (T, ⊻). Not yet checked with rejig: the two .p47 should be the same size.

## Oct 24, 2026 - v0.2.0: the truth table, key 6 (Victor)

- 64 rows fit on one screen in the small font (GRFNT 10: 6 columns a character, 9 rows a line): four columns of
  16 rows, each " 1 0 1 1 0 1 | 1" (90 columns) at x 2 + 99 c, a header " p q r s t u | f" over each; the formula on top.
- LBL :TABLE: only after a verdict (R96 = 1; 0 after F1-F6, delete, clear, a syntax error). The variables used in
  order p..u (their code letters in R47); row k = 2^n - 1 down to 0, the j-th variable used = bit n - 1 - j of k
  (the first one changing slowest, all true first, as in the books); the word's bit m = sum of 2^code of the true
  ones, read with BS? IND. LBL / DSE / GTO loops (the 10 DO are used), the key wait LBL / PAUSE 50 / KEY? / GTO.
  Back: the soft keys, the formula and the verdict drawn again.
- 1 413 steps for 8 rows, 16 029 for 64 (about 2.7 s on a C47). R-CLR now R20-R96.
- The verdict's examples on two lines (T: row 60, F: row 40; the verdict at 100, the rows at 80): with six
  variables "T: p=0 ... u=0  F: ..." ran past the screen's width into the key hints.
- Victor: the value column headed Φ (capital phi, the formula; was f, mixed up with F: false; the small font's φ
  looks odd), and BLOCK 1-4 under the blocks of 16 rows (5 or 6 variables): the four headers read as four tables.
- Tests: the table of 8 formulas against the Python evaluator (and its BLOCK labels), key 6 ignored before 5,
  after a change and after a syntax error. docs/LOGIC47_table3.png, LOGIC47_table6.png. 982 steps, about 3.5 KB;
  DO 10, IF 0.

## To do

1. Run on Victor's C47: the bitwise commands first.
2. Ideas: show the truth table (scroll), equivalence of two formulas, normal forms (DNF / CNF), v w (7-8
   variables: two or four words).
