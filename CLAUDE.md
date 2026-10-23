# Logic 47: working rules

- Work on a new branch; Victor creates and merges the PRs. Never force-push or rewrite history.
- Commit author: "Victor Valdes" <valdesvj@users.noreply.github.com>.
- Never commit binaries (.p47 files made by rejig).
- Edit the program in programs_rem/LOGIC47.txt (commented source), then run python3 tools/build_logic47.py:
  it writes programs/, build/ and listings/. Never edit those three by hand.
- STRUCT as Elements 47: IF / ELSE / ENDIF, DO / WHILE / ENDDO, indented, no numbers in the source; a test
  right before IF / WHILE; never a test before ELSE, ENDIF, DO, ENDDO. At most 10 IF and 10 DO (the original
  DM42; LOGIC47 has 10 DO). Named labels LBL :NAME:; LBL 68-73 are the connectives (XEQ IND, 60 + code).
- Text on the C47 screen: ATEXT in GRFNT 21 (GRFNT 10 for the small text). Restore GRFNT 20 and GRMOD 0 before
  the program ends. GRMOD and GRFNT take X: write `3 GRMOD`.
- Key waits: DO / PAUSE 50 / KEY? 23 / WHILE / ENDDO (as Elements 47). The soft keys F1-F6: KEY? codes 11-16.
- Only commands already run on a C47 in Almanac 47 or Elements 47, except the bitwise ones (AND OR XOR NOT BS?
  BC?), new here: say so in the README until Victor has run them; a new command: ask Victor to try it.
- Check every change in the simulator (python3 python/logic47sim.py) and with python3 tests/test_logic47.py.
- python/c47sim.py, stdfont.py, tinyfont.py come from Almanac 47; the bitwise commands are added at the end of
  its run loop (marked logic47). A fix is made in Almanac 47 first, then copied here; the bitwise block is to be
  taken there too.
- Work in one repository at a time (this one); almanac47, elements47 and zones47 are for reference only.
- Ask before anything that can't be undone. Pull requests only for logic47.
