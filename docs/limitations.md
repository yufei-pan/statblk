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

### `--check` can skip a disk's SMART where a row is dropped for another reason
- Kind: deferred
- What the operator sees: `statblk --check` reads SMART only from the rows the table keeps, so a failing disk
  whose row is dropped passes with exit 0 and no output, with no stopped command involved, in these cases: on
  macOS with `-o NAME,FSUSE%,SMART` (no `diskutil` runs without a column that needs it, so an unmounted disk has
  no SIZE and its row goes); on Linux with no `lsblk` installed and `-F` (an unmounted filesystem's FSTYPE is
  blank, so its row goes); on macOS with `-A` (throughput is always 0 there, so every device counts as idle); a
  device whose SIZE reads 0 (unless `--show_zero_size_devices`). A stopped `mount` does the same on macOS without
  `-M` when only SMART is checked (`-x FSUSE%`): a mounted filesystem it did not list keeps its row only if
  `diskutil` gave the device a SIZE (and, with `-F`, an FSTYPE), and with `-o` naming no `diskutil` column it
  cannot.
- Why: a filter or a missing value that drops a row takes its SMART with it. Reproduced in 1.62's reviews with the
  real `main()` and fake commands, not on a failing disk; 1.61 did the same.
- Revisit when: statblk 1.63, started right after 1.62, after the `diskutil` parser (read every section). The plan is to
  decide whether `--check` judges each disk's SMART before filters and a zero size drop its row; that would also
  shrink the cut rule in `main()` to `mount` and FSUSE%, and it is the question to settle before the table is
  patched again.

### `--check` can count a stopped command that hid nothing it reads
- Kind: deferred
- What the operator sees: a run with no problem exits 3 and names the stopped command although every checked row
  was there, in a few combinations: a pattern (not `-D`) with any stopped command; `-v` with no pattern, or a `-D`
  that matches no device, with a stopped `diskutil` or `mount`; `--show_zero_size_devices` with a stopped
  `diskutil` (macOS). A larger `-t` clears it, as the line says. 1.61 exited 0 in these runs, as it did in the
  ones where the stopped command did hide a failing disk.
- Why: the cut rule in `main()` is a fixed table of what each command can hide; where flags make that moot, or
  where a pattern's match depends on the missing values, it errs to "could not tell".
- Revisit when: statblk 1.63, with the `--check` design question in the entry above.
