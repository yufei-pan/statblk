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

### `--check -v` with no pattern judges nothing
- Kind: deferred (1.65)
- What the operator sees: `statblk --check -v` (invert, but no pattern) matches no row, so it checks no disk and exits 0 with nothing printed. 1.63 did the same.
- Why: the inverted match is applied to the patterns; with none there is nothing to keep. The right answer is exit 3 ("could not tell"), which is one more rule in `main()`.
- Revisit when: 1.65.

### `--check` with no valid output field judges nothing
- Kind: deferred (1.65)
- What the operator sees: `statblk --check -x FSUSE%,SMART -o foo` (every field it would show is unknown or excluded) prints "Ignoring invalid output field: FOO." then "No valid output fields specified.", gets no rows, and exits 0. 1.63 did the same.
- Why: `get_drives_info()` returns no rows and `check_rows([])` calls that healthy. The right answer is exit 3.
- Revisit when: 1.65.

### `-w` with stderr redirected and stdout a terminal repeats the note each refresh
- Kind: deferred (1.65)
- What the operator sees: `statblk -w 2 2>>log` on a terminal writes the stopped, missing or failed command's note to the log on every refresh. 1.63 did the same for a stopped or missing command.
- Why: the note is repeated when the table is redrawn on a terminal (stdout), so it stays under the table; it is not keyed on where stderr goes. It should be once per run when stderr is not that terminal.
- Revisit when: 1.65.

### A counter reset between refreshes shows a negative READ or WRITE rate
- Kind: deferred (1.65)
- What the operator sees: in watch mode, a device whose kernel counters reset (a device removed and re-added under the same name, a wrapped counter) shows one refresh with a negative rate (`null` in `-J`). 1.63 did the same.
- Why: the rate is the difference of two samples over the interval, with no check that the second is not below the first. It should be blank for that refresh.
- Revisit when: 1.65.
