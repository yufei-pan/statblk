# statblk: progress

Open work lives here and nowhere else (RULES, "Long work: the progress file"). Edit rows in place, in the commit that changes the work.

## Goal
- 2026-11-05, for every cas tool: "we improve the cas scripts iteratively. feel free to add scope / tasks if when doing some work, you noticed some other thing that can be improved with cas scripts." (the user; no goal for this repo alone is written in the repo)

## Open work

### statblk 1.64 (no written plan yet: the entries of kind "deferred (1.64)" in docs/limitations.md, written in 1.63's fix round; next, after 1.63's release on 2026-11-17)
- **The 1.63 reviews' deferrals,** each with its plan in docs/limitations.md (a mount or lsblk that fails without being stopped recorded as not answered in full; `-F` with no lsblk says so; macOS APFS type case; `Volume Total Space`; Linux `-F` per device; an unreadable sysfs stat or size; Linux `-A` with `-P`; a macOS mount source with a space; macOS READ/WRITE never read; the Mac test's margin). State: built on feat/164 at 4dc4bef (2026-11-20, worktree .worktrees/statblk-164; builder b164: all 11 entries settled, suites 549 passed on 3.6, 3.9, 3.11, 3.12 and 3.14, the Mac 547 passed); final review fr164 (Fable high, with nine second opinions) running since 13:25. From: 1.63's final review and second opinions (2026-11-16), deferrals, not asked.
- **The embedded multiCMD 1.68** (released 2026-11-17, tag v1.68). State: built on feat/164 (c2c28c0, the paste matches v1.68's file byte for byte), in review (fr164).
- **The `--check` help's two loose clauses** (exit 1 also prints the unknown rows; a healthy `-j` prints the header row, `-J` prints `[]`): one-line fix. State: built on feat/164 (b0b0982), in review (fr164). From: 1.63's re-review second opinion (docsA 12), a deferral.

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
- None now. Decided 2026-11-16, chief's decision C78 (not the user's words; the user may reverse it): a disk that reports zero size is a known limitation with one README line (option 1 of the question from 1.62's last review); written and released in 1.63.

## Closed
- 1.63 (tag v1.63, the merge of feat/163, released 2026-11-17): `--check` judges what it can read. A filter drops a row only on a value that was read (macOS lists an unmounted device with SIZE blank when `diskutil` gave none; `-F` keeps a device whose type could not be read; macOS `-A` filters nothing; a mount whose statvfs fails shows FSUSE% `ERROR` and `--check` counts it unknown); macOS reads every section of `diskutil info -all` (20 devices on the test Mac where 1.62 listed 8); the cut rule shrinks to two terms; "no media" reads as 0; diskutil answered only at exit 0; 130 exit-level tests through the real `main()` (379 in all). The zero-size disk is a known limitation (chief's decision C78, 2026-11-16). Design check dc163 (taken), build b163, final review fr163 (release; fix round taken for the statvfs case), fix round f163, re-review rr163 (release), tests-and-docs commit f163b; PyPI wheel 01066784 and sdist 20ab51de match the build; GitHub release v1.63. cas-toolbox takes it in the week-48 roll-up.
- 1.62 (tag v1.62, the merge of feat/162, released 2026-11-15): a `diskutil`, `mount` or `lsblk` that `--timeout` stopped is named on stderr; in `--check` one that can hide what the check reads makes a run with no problem exit 3 (1.61 exited 0); the statvfs thread starts with one C call, so a Ctrl-C on Python 3.6 no longer hangs `statblk -w`; `STATVFS_MIN_WAIT`'s measured reason; the embedded multiCMD 1.67; no multiCMD install requirement (the user's pick 2026-11-14, "Drop it, as hpcp did (Recommended)"); Python 3.11 in CI; the lessons header's 80 KB rule. Built on feat/162; final review fix first (a healthy `--check` printed the note), fix round 1 (116542a to 58494d8), re-review release with -M regressions found by second opinions, fix round 2 rebuilt the rule as one table (271bd41 to ebc8fe7), re-review release; texts c02583b, deferrals ebc8fe7 and 6a03269.
- macOS `-t 0` gives `diskutil` and `mount` no limit: done in f184ad5, v1.61 (the main session's older note still lists it as open).
