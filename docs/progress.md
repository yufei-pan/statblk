# statblk: progress

Open work lives here and nowhere else (RULES, "Long work: the progress file"). Edit rows in place, in the commit that changes the work.

## Goal
- 2026-11-05, for every cas tool: "we improve the cas scripts iteratively. feel free to add scope / tasks if when doing some work, you noticed some other thing that can be improved with cas scripts." (the user; no goal for this repo alone is written in the repo)

## Open work

### statblk 1.63 (no written plan; from the 1.62 reviews)
- **A design check of `--check` first.** State: running since 2026-11-16 ~22:05 on account b (a fresh agent; scratchpad notes dc163). The cut rule in `main()` (a table of what each stopped command can hide) drew findings in every 1.62 round, so per RULES "Step back when findings repeat" no further fix goes into it before a fresh agent answers two questions: is the table needed, and can `--check` lose the state the findings need. The candidate: judge each disk's SMART and each mounted filesystem's FSUSE% before rows drop for missing data, so that only the operator's own filters narrow the check; the table would then shrink to `mount` and FSUSE%. Its options go to the user only if they change what gets built or drop something the user asked for. Covers the deferred entries "`--check` can skip a disk's SMART where a row is dropped for another reason" and "`--check` can count a stopped command that hid nothing it reads" in docs/limitations.md. From: the 1.62 re-reviews (the main session's plan, 2026-11-15).
- **macOS: read every section of `diskutil info -all`.** State: not started; after the design check, because the table assumes diskutil's SIZE. Where: `get_macos_diskutil_info()` ends a device at its first blank line; a device ends where the next one's `Device Node` starts (the 1.62 re-review tried this on the test Mac: 20 of 20 devices get a size, the table grows from 8 to 20 rows). Replace the test fixture with real, anonymised `diskutil info -all` output from macOS 26 (two or more devices with every section), add a test that an unmounted whole disk gets its SIZE, and say in the README's macOS section that every device is listed. Also the deferred entry "macOS: only the first section of each device in `diskutil info -all` is read". From: the 1.62 re-review (a deferral, not asked).
- **Tests through the real `get_drives_info()` for the `--check` cases.** State: not started. tests/test_check.py's cells fake `get_drives_info()` and restate the table, so a wrong entry passes; the cases the design check keeps get tests with fake commands under the real `get_drives_info()`. From: the 1.62 second opinions.

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
- 1.62 (tag v1.62, the merge of feat/162, released 2026-11-15): a `diskutil`, `mount` or `lsblk` that `--timeout` stopped is named on stderr; in `--check` one that can hide what the check reads makes a run with no problem exit 3 (1.61 exited 0); the statvfs thread starts with one C call, so a Ctrl-C on Python 3.6 no longer hangs `statblk -w`; `STATVFS_MIN_WAIT`'s measured reason; the embedded multiCMD 1.67; no multiCMD install requirement (the user's pick 2026-11-14, "Drop it, as hpcp did (Recommended)"); Python 3.11 in CI; the lessons header's 80 KB rule. Built on feat/162; final review fix first (a healthy `--check` printed the note), fix round 1 (116542a to 58494d8), re-review release with -M regressions found by second opinions, fix round 2 rebuilt the rule as one table (271bd41 to ebc8fe7), re-review release; texts c02583b, deferrals ebc8fe7 and 6a03269.
- macOS `-t 0` gives `diskutil` and `mount` no limit: done in f184ad5, v1.61 (the main session's older note still lists it as open).
