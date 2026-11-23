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
- What the operator sees: statblk hides a device whose size reads 0 (an empty card-reader slot, empty virtual media) unless `--show_zero_size_devices`. A partition row carries its parent's SMART, so a failing disk is still judged through any partition row that is shown; a whole disk of size 0 with no partition row shown goes unjudged by a plain `statblk --check` (exit 0, nothing printed). `statblk --check --show_zero_size_devices` judges it.
- Why: the zero-size rule keeps an empty slot from showing as a disk, and `--check` judges the rows the table shows. Reproduced with fake commands only, not on a real disk; 1.62 and 1.61 did the same.
- Revisit when: someone sees it on a real disk, or measures what smartctl answers for one.
- Approved: 2026-11-16, chief's decision C78 (the user's desk session; not the user's words): option (1), a known limitation with one README line.

### `--check` on a host that lists no block device exits 0
- Kind: deferred (1.66)
- What the operator sees: `statblk --check` on a host where no block device is listed (`/sys/class/block` empty or not readable, or a host with only non-block mounts) prints nothing and exits 0, though nothing was judged. 1.64 and 1.65 do the same.
- Why: `get_blocks()` swallows a failed listing of `/sys/class/block`, and `check_rows()` calls a table with no rows healthy. Plan for 1.66: a failed listing counts as a source that could not be read (exit 3 when nothing else is wrong, as a failed command does since 1.62), and a run with no filter that lists no device says "Nothing was checked" and exits 3. A filter that leaves no row on a host that does list devices stays the operator's own question (exit 0).
- Revisit when: 1.66.
