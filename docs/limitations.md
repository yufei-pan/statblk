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

### macOS: only the first section of each device in `diskutil info -all` is read
- Kind: deferred
- What the operator sees: on macOS, a device that has no mounted filesystem (the internal SSD's disk0, an
  unmounted external disk) is not listed, and `statblk --check` does not see its SMART; UUID, LABEL, SERIAL and
  an unmounted device's FSTYPE are blank and DISCARD is N/A. Mounted filesystems are listed as before.
- Why: `diskutil info -all` splits each device into sections with blank lines, and statblk ended a device at
  the first one. Seen on macOS 26.6.2, 2026-11-15; 1.61 did the same.
- Revisit when: statblk 1.63, started right after 1.62.

### `--check` can skip a disk's SMART where a row is dropped for another reason
- Kind: deferred
- What the operator sees: `statblk --check` reads SMART only from the rows the table keeps, so a failing disk
  whose row is dropped passes with exit 0 and no output, with no stopped command involved, in three cases: on
  macOS with `-o NAME,FSUSE%,SMART` (no `diskutil` runs without a column that needs it, so an unmounted disk has
  no SIZE and its row goes); on Linux with no `lsblk` installed and `-F` (an unmounted filesystem's FSTYPE is
  blank, so its row goes); on macOS with `-A` (throughput is always 0 there, so every device counts as idle).
- Why: a filter or a missing value that drops a row takes its SMART with it. Reproduced in 1.62's reviews with the
  real `main()` and fake commands, not on a failing disk; 1.61 did the same.
- Revisit when: statblk 1.63, started right after 1.62, together with the `diskutil` parser above. The plan is to
  decide whether `--check` judges each disk's SMART before filters and a zero size drop its row; that would also
  shrink the cut rule in `main()` to `mount` and FSUSE%, and it is the question to settle before the table is
  patched again.
