# Limitations

Approved known limitations and deferrals. Reviewers: read this first, and don't raise these again.

### The stuck-smartctl check sees only processes in statblk's /proc
- Kind: known limitation
- What the operator sees: statblk 1.58 starts no new smartctl on a disk where one older than `--timeout` is still
  running, but it can only find that one in its own `/proc`. Two cases where it can't: `/proc` mounted with
  `hidepid` (common on shared nodes), where a non-root user running `statblk --sudo -w` or a non-root cron
  `statblk --sudo --check` cannot see the stuck smartctl, which runs as root; or statblk in a fresh container with its
  own process namespace (a stuck smartctl from earlier runs or from the host is not visible). There, as in 1.57,
  each refresh or run whose smartctl gets stuck adds one more stuck process.
- Why: nothing statblk can do makes `/proc` show processes the kernel hides from it.
- Revisit when: someone runs statblk that way on a host with a dying disk.
- Approved: 2026-10-29, the user chose "Known limitation (Recommended)".

### `--check` does not judge a whole disk whose size reads zero
- Kind: known limitation
- What the operator sees: statblk hides a device whose size reads 0 (an empty card-reader slot, empty virtual media) unless `--show_zero_size_devices`. A partition row carries its parent's SMART, so a failing disk is still judged through any partition row that is shown; a whole disk of size 0 with no partition row shown goes unjudged by a plain `statblk --check` (exit 0, nothing printed; when it is the only block device the table has no row left, and the run exits 3 with `Nothing was checked: no block device is listed or shown`, and from 1.66 also when no other row holds a value, with `no row holds a value in FSUSE% or SMART`). `statblk --check --show_zero_size_devices` judges it.
- Why: the zero-size rule keeps an empty slot from showing as a disk, and `--check` judges the rows the table shows. Reproduced with fake commands only, not on a real disk; 1.62 and 1.61 did the same.
- Revisit when: someone sees it on a real disk, or measures what smartctl answers for one.
- Approved: 2026-11-16, chief's decision C78 (the user's desk session; not the user's words): option (1), a known limitation with one README line.

### A spun-down SAS disk reads `UNKNOWN`, not `STANDBY`
- Kind: deferred (1.67)
- What the operator sees: for a SCSI/SAS disk, smartctl 7.5 prints `Device is in STANDBY BY TIMER mode, exit(2)`, `STANDBY BY COMMAND`, `STANDBY_Y BY TIMER`, `STANDBY_Y BY COMMAND` or `LOW POWER` when `-n standby` skips a spun-down disk (scsiprint.cpp:3545 to 3575 at RELEASE_7_5; read from its source, not seen on a real disk). `SMART_STANDBY_RE` (`device is in (sleep|standby)\w* mode`) matches none of them, so the `SMART` cell reads `UNKNOWN` and `--check` exits 3 and lists the disk, where a SATA disk in `STANDBY` is healthy. Never a false 0, and the same in 1.65 and 1.66.
- Why: found by the 1.66 final review, outside that version's two entries; a change to the parser needs its own tests and review.
- Plan: 1.67 changes the pattern to `device is in (sleep|standby|low power)[\w ]* mode`, with one test fixture line per form above, taken from smartctl's source.
- Revisit when: 1.67.
