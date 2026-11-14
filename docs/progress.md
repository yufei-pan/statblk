# statblk: progress

Open work lives here and nowhere else (RULES, "Long work: the progress file"). Edit rows in place, in the commit that changes the work.

## Goal
- 2026-11-05, for every cas tool: "we improve the cas scripts iteratively. feel free to add scope / tasks if when doing some work, you noticed some other thing that can be improved with cas scripts." (the user; no goal for this repo alone is written in the repo)

## Open work

### statblk 1.62 (no written plan; the main session's list from the 1.61 reviews)
- **Report a `diskutil` or `mount` that `--timeout` cut (exit 124).** State: not started. Where: `get_macos_diskutil_info()` and `parseMount()` in statblk.py read the output and ignore the exit status, so the columns come out blank, nothing is on stderr and `--check` prints nothing and exits 0. Fix: a warning on stderr for a 124 from either, and in `--check`. This is also the deferred entry "A diskutil or mount cut by `--timeout` on macOS leaves blank columns with no message" in docs/limitations.md ("Revisit when: the next statblk release", noted 2026-11-11 from the 1.61 final review; the entry stays there until the fix ships). From: a deferral, not asked.
- **`_statvfs_with_timeout()` starts a `threading.Thread` on the main thread for every mount at every refresh.** State: not started (a check first). Where: statblk.py, `_statvfs_with_timeout` (`thread = threading.Thread(...)`, then `thread.start()`). multiCMD 1.60 moved off this pattern: on the main thread a Ctrl-C, or what a signal handler raises, can land inside `Thread.start()` and leave `threading`'s lock or the new thread's `_started` Event held, so every later thread start hangs (multiCMD README, "Upgrading to 1.60"; its fix starts threads with `_thread.start_new_thread` or on a helper). Decide whether `statblk -w` is exposed (Ctrl-C is how it is stopped); if so, fix it the same way, otherwise write it down as a known limitation (needs the user's OK). From: the main session's plan (2026-11-11).
- **`STATVFS_MIN_WAIT = 0.5` needs a measured reason.** State: not started. Where: statblk.py, next to `STATVFS_MIN_WAIT`; its comment says what the floor is for (healthy mounts still get answered after a stuck smartctl has used up the refresh deadline) but gives no measurement. RULES principle 11: write the reason next to the number, or change the number. From: the main session's plan (2026-11-11).
- **Add Python 3.11 to the CI matrix.** State: not started. Where: .github/workflows/test.yml has 3.9, 3.12, 3.14 and the 3.6 container; no 3.11. Adds `"3.11"` to the matrix list. From: the user, 2026-11-12: "Add 3.11 to CI (Recommended)", for every repo's next release.
- **Embed multiCMD 1.66.** State: not started (multiCMD 1.66 was released 2026-11-14). Where: statblk.py embeds 1.61 (gate `< (1, 61)` at the top of the file). Paste the `multiCMD_min_zlib_a85.py` block from the 1.66 tag (not a fresh regeneration), update the gate, and the README's "The embedded multiCMD is now ..." note. From: the main session's plan.
- **Drop `install_requires` multiCMD.** State: not started; done together with hpcp and statbtrfs. Where: setup.py `install_requires=['multiCMD>=1.56']`; README line 27 ("Requires ... the multiCMD package (>= 1.56)") and the pip 9 `-U` notes in the "Upgrading to ..." sections go with it. Why: the embedded copy makes the dependency moot, and it is what makes pip 9 (stock on EL7 and EL8) stop `pip3 install -U statblk` when multiCMD 1.57 or earlier is installed. From: the main session's plan (2026-11-11).

### Standing rows
- **Deferred work** is in `docs/limitations.md` (entries of kind "deferred"); each names when it is revisited.

## Questions waiting for the user
- None.

## Closed
- macOS `-t 0` gives `diskutil` and `mount` no limit: done in f184ad5, v1.61 (the main session's older note still lists it as open).
