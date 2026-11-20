# Limitations

Approved known limitations and deferrals. Reviewers: read this first, and don't raise these again.

### The stuck-smartctl check sees only processes in statblk's /proc
- Kind: known limitation
- What the operator sees: statblk 1.58 starts no new smartctl on a disk where one older than `--timeout` is still
  running, but it can only find that one in its own `/proc`. Two cases where it can't: `/proc` mounted with
  `hidepid` (common on shared nodes) and a non-root user running `statblk --sudo -w` or a non-root cron
  `statblk --sudo --check` (the stuck smartctl runs as root and is hidden); or statblk in a fresh container with its
  own process namespace (a stuck smartctl from earlier runs or from the host is not visible). There, as in 1.57,
  each refresh or run whose smartctl gets stuck adds one more stuck process.
- Why: nothing statblk can do makes `/proc` show processes the kernel hides from it.
- Revisit when: someone runs statblk that way on a host with a dying disk.
- Approved: 2026-10-29, the user chose "Known limitation (Recommended)".

### `--check` does not judge a whole disk whose size reads zero
- Kind: known limitation
- What the operator sees: statblk hides a device whose size reads 0 (an empty card-reader slot, empty virtual media) unless `--show_zero_size_devices`. A partition row carries its parent's SMART, so a failing disk is still judged through any partition row that is shown; a whole disk of size 0 with no partition row shown goes unjudged by a plain `statblk --check` (exit 0, nothing printed). `statblk --check --show_zero_size_devices` judges it.
- Why: the zero-size rule keeps an empty slot from showing as a disk, and `--check` judges the rows the table shows. Reproduced with fake commands only, not on a real disk; 1.62 and 1.61 did the same.
- Revisit when: someone sees it on a real disk, or measures what smartctl answers for one.
- Approved: 2026-11-16, chief's decision C78 (the user's desk session; not the user's words): option (1), a known limitation with one README line.

### macOS: a mount line with a space in its source, or " (" in its mount point, is misread (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: with `-P`, a network mount whose source has a space (`//user@server/My Share on /Volumes/My Share (smbfs, ...)`) never becomes a row. A volume whose name has " (" in it (`/Volumes/Backup (old)`) is read at a cut-short mount point, so its statvfs fails: FSUSE% `ERROR`, and a healthy `--check` exits 3 (1.62 left the volume out of the table and its space unchecked, exit 0). Seen with a faked `mount` line (macOS `mount(8)`'s format), not on a Mac.
- Why: `parse_darwin_mount_line()` reads the source as one word (`\S+`) and the mount point up to the first " (".
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): read the source up to ` on ` and the options from the last parenthesis (`^(.+?)\s+on\s+(.+)\s+\(([^()]*)\)$`), with a test on each line. On Linux, read mountinfo with `errors='surrogateescape'`, so a non-UTF-8 mount path reaches statvfs intact.

### The macOS test of a silent `diskutil` and `mount` has a thin time margin (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: nothing; on the test Mac `test_a_silent_diskutil_and_mount_are_stopped_and_recorded` failed once on a first run (and passed in 19 further runs), because it gives the fake commands 0.3 s to print a first line, and a fresh script there takes 0.09 to 0.12 s to print it. The cause is likely, not proven: the measured latency explains a margin of 3x, not the one run over 0.3 s.
- Why: the comment in the test says 15 times what the test needs, which holds on Linux (0.02 s measured) and not on the Mac.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): a test-only fix with a margin measured on the Mac, and the comment corrected.
