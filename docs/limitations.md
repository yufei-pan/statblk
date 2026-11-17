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

### `--check` skips the SMART of a disk whose size reads zero
- Kind: deferred
- What the operator sees: a device whose size reads 0 is hidden unless `--show_zero_size_devices`, so a plain
  `statblk --check` does not judge its SMART, and a failing disk that reports zero size passes with exit 0 and no
  output. `statblk --check --show_zero_size_devices` judges it. 1.63 narrowed this entry to that case: a value
  statblk could not read no longer drops a row.
- Why: statblk hides zero-size devices (an empty card-reader slot, empty virtual media) by default. Reproduced with
  fake commands only, not on a real disk; 1.62 and 1.61 did the same.
- Revisit when: the user's answer to the zero-size question (docs/progress.md, questions).
