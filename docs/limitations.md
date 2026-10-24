# Limitations

Approved known limitations and deferrals. Reviewers: read this first, and don't raise these again.

### lsblk-missing note wiped in watch mode
- Kind: deferred
- What the operator sees: with no `lsblk` installed, `statblk -w N` on a terminal prints "lsblk not found …" to
  stderr on each refresh, and the next screen redraw wipes it at once, so the reason FSTYPE, UUID, MODEL and
  SERIAL are incomplete is never visible. Piped output shows the line once per refresh. 1.55 behaved the same
  with multiCMD's "Command path not found" line.
- Why: found in the 1.56 release review; fixing it (print the note once per run, below the table) waits for
  the simplification pass.
- Revisit when: the simplification pass over statblk.
- Approved: 2026-10-23, the user chose "Fix later, in the simplify pass".
