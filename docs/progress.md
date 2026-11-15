# statblk: progress

Open work lives here and nowhere else (RULES, "Long work: the progress file"). Edit rows in place, in the commit that changes the work.

## Goal
- 2026-11-05, for every cas tool: "we improve the cas scripts iteratively. feel free to add scope / tasks if when doing some work, you noticed some other thing that can be improved with cas scripts." (the user; no goal for this repo alone is written in the repo)

## Open work

### statblk 1.62 (no written plan; the main session's list from the 1.61 reviews)
- **Built; under final review (2026-11-15):** branch feat/162 (worktree statblk-162) at 8e95d03, 2a717fd to 8e95d03: every row below is built, the suites pass on 3.14, 3.11 and 3.6 (first runs), pip 9 upgrades over an old multiCMD, the docs/lessons.md header follows the template's 80 KB rule (paused 2026-11-14 at the user's ask; resumed on chief's order after the user's "Resume both (Recommended)"). Final review (2026-11-15): fix first. A healthy `--check` printed a cut note, a cut diskutil could hide a failing unmounted disk from `--check` (as in 1.61, but the closed deferral planned `--check` too), and the note repeated on every `-w` refresh; plus docs and tests. Next: fix round 1 (running), then a re-review, then the release (COMMIT_DATE at the release commit).
- **Report a `diskutil` or `mount` that `--timeout` cut (exit 124).** State: not started. Where: `get_macos_diskutil_info()` and `parseMount()` in statblk.py read the output and ignore the exit status, so the columns come out blank, nothing is on stderr and `--check` prints nothing and exits 0. Fix: a warning on stderr for a 124 from either, and in `--check`. This is also the deferred entry "A diskutil or mount cut by `--timeout` on macOS leaves blank columns with no message" in docs/limitations.md ("Revisit when: the next statblk release", noted 2026-11-11 from the 1.61 final review; the entry stays there until the fix ships). From: a deferral, not asked.
- **`_statvfs_with_timeout()` starts a `threading.Thread` on the main thread for every mount at every refresh.** State: not started (a check first). Where: statblk.py, `_statvfs_with_timeout` (`thread = threading.Thread(...)`, then `thread.start()`). multiCMD 1.60 moved off this pattern: on the main thread a Ctrl-C, or what a signal handler raises, can land inside `Thread.start()` and leave `threading`'s lock or the new thread's `_started` Event held, so every later thread start hangs (multiCMD README, "Upgrading to 1.60"; its fix starts threads with `_thread.start_new_thread` or on a helper). Decide whether `statblk -w` is exposed (Ctrl-C is how it is stopped); if so, fix it the same way, otherwise write it down as a known limitation (needs the user's OK). From: the main session's plan (2026-11-11).
- **`STATVFS_MIN_WAIT = 0.5` needs a measured reason.** State: not started. Where: statblk.py, next to `STATVFS_MIN_WAIT`; its comment says what the floor is for (healthy mounts still get answered after a stuck smartctl has used up the refresh deadline) but gives no measurement. RULES principle 11: write the reason next to the number, or change the number. From: the main session's plan (2026-11-11).
- **Add Python 3.11 to the CI matrix.** State: not started. Where: .github/workflows/test.yml has 3.9, 3.12, 3.14 and the 3.6 container; no 3.11. Adds `"3.11"` to the matrix list. From: the user, 2026-11-12: "Add 3.11 to CI (Recommended)", for every repo's next release.
- **Embed multiCMD 1.67.** State: not started (multiCMD 1.67 was released 2026-11-14). Where: statblk.py embeds 1.61 (gate `< (1, 61)` at the top of the file). Paste the `multiCMD_min_zlib_a85.py` block from the 1.67 tag (not a fresh regeneration), update the gate, and the README's "The embedded multiCMD is now ..." note. From: the main session's plan.
- **Drop `install_requires` multiCMD.** State: not started; the user's pick 2026-11-14, "Drop it, as hpcp did (Recommended)" (their 2026-11-06 pick had kept the floor at 1.56; hpcp dropped it in 9.89). Where: setup.py `install_requires=['multiCMD>=1.56']`; README line 27 ("Requires ... the multiCMD package (>= 1.56)") and the pip 9 `-U` notes in the "Upgrading to ..." sections go with it. Why: the embedded copy makes the dependency moot, and it is what makes pip 9 (stock on EL7 and EL8) stop `pip3 install -U statblk` when multiCMD 1.57 or earlier is installed. From: the main session's plan (2026-11-11).

### Standing rows
- **Deferred work** is in `docs/limitations.md` (entries of kind "deferred"); each names when it is revisited.

## Standing decisions
The user's rulings on how the cas repos are worked, one line each; a line changes only on the user's word. The cas monorepo's CLAUDE.md holds the same list, with how to reach the test machines.
- Deferrals (2026-11-05): "please do not ask me about features you think should defer to next version anymore. instead, note them down and after getting the current version done, start the next version right away. only ask me to approve things that are going into limitations that we do not have plans to fix it any time soon."
- The release gate (2026-11-09): "releasing a new version gate is only if it does not make an existing issue worse. even if the fix does not completely resolve the problem, if it makes the result more tolerable, we shall not gate it for release because there are still issues."
- Review before upload (2026-10-18): "commit and push is fine but when packaging, please follow the rule that need a code review before uvpack / upload to pypi".
- A test that passed only on a rerun (2026-11-06, "Green with a warning (Recommended)"): CI stays green with a warning, and "Before any upload, every such test still needs a written cause either way."
- Release pushes (2026-11-10, "Release OK covers it (Recommended)"): an OK for a release covers its push of main, the version tag and the GitHub release.
- Tests (2026-11-12, "Core per release, full at roll-up (Recommended)"): CI's own command on Python 3.14 and 3.11 in Docker before each release; the full gate (every Python in CI, macOS, EL7 on Python 3.11) before a Monday roll-up pin moves.
- CentOS 7 (2026-11-04): "for centos 7, which is already EOL, we only target all the last packages released for it. this also includes EPEL which is also in archive right now."
- EL8 (2026-11-05): "yes rocky 8 it is. let's also only test on them when you think test on real kernel is needed."
- macOS (2026-11-11): tests run on the user's own always-on Mac, as a standard user made for them, never with sudo.

## Questions waiting for the user
- None.

## Closed
- macOS `-t 0` gives `diskutil` and `mount` no limit: done in f184ad5, v1.61 (the main session's older note still lists it as open).
