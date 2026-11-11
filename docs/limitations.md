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

### A diskutil or mount cut by `--timeout` on macOS leaves blank columns with no message
- Kind: deferred
- What the operator sees: on macOS, a `diskutil info -all` or `mount` that prints nothing for longer than `-t` is cut
  (exit 124), and its columns (SIZE, MODEL, FSTYPE, MOUNTPOINT and others), or whole rows, come out blank, with nothing
  on stderr and exit 0. `statblk --check` then prints nothing and exits 0, which reads as healthy. On the test Mac
  `diskutil` is silent for 0.5 to 0.6 s of its 1 s run, so the 2 s default has about 3x room; `-t 0.5` blanks MODEL on
  five rows (1.60 and 1.61 alike).
- Why: `get_macos_diskutil_info` and `parseMount` read the output and ignore the exit status. Found by the 1.61 final
  review; not this release's change (1.61 gives `mount` 2 s by default where 1.60 gave 1 s).
- Revisit when: the next statblk release: report a 124 from either as a warning on stderr, and in `--check`.
- Noted: 2026-11-11, from the 1.61 final review; a deferral, not asked.
