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
- What the operator sees: statblk hides a device whose size reads 0 (an empty card-reader slot, empty virtual media) unless `--show_zero_size_devices`. A partition row carries its parent's SMART, so a failing disk is still judged through any partition row that is shown; a whole disk of size 0 with no partition row shown goes unjudged by a plain `statblk --check` (exit 0, nothing printed; when it is the only block device the table has no row left, and the run exits 3 with `Nothing was checked: no block device is listed or shown`). `statblk --check --show_zero_size_devices` judges it.
- Why: the zero-size rule keeps an empty slot from showing as a disk, and `--check` judges the rows the table shows. Reproduced with fake commands only, not on a real disk; 1.62 and 1.61 did the same.
- Revisit when: someone sees it on a real disk, or measures what smartctl answers for one.
- Approved: 2026-11-16, chief's decision C78 (the user's desk session; not the user's words): option (1), a known limitation with one README line.

### `-D` matches the device path, so an anchored name finds nothing
- Kind: deferred (1.66)
- What the operator sees: `-D` applies its pattern to the device path (`/dev/sda`; a device-mapper device also by `/dev/mapper/<name>`), not to the name the table shows, so `-D '^sda$'` matches nothing and `statblk -D '^sda$'` prints only the header. Under `--check` that run exits 3 with `Nothing was checked: no row is left to judge after the filters (a -D pattern).` (1.64 exited 0, over a failing disk too). The README's `-D` row says what it matches.
- Why: the code has searched the path since before 1.64 (`get_drives_info()` tests the device and `get_mapper_path(device)`), while the docs said "device names". Changing what an existing pattern matches is a behaviour change that needs its own version. Plan for 1.66: also match the kernel name (`sda`) and the mapper name (`pve-root`) as the NAME column shows them, and keep matching the path, so no pattern that matches today stops matching; a `-D -v` pattern can then drop a row it kept (`-D -v '^s'` keeps every row now), which the README and the release notes say.
- Revisit when: 1.66.

### `--check` counts a row with no value to check as healthy
- Kind: deferred (1.66)
- What the operator sees: a row whose `FSUSE%` and `SMART` are both blank (an unmounted loop, zram or device-mapper device: no SMART, no mount) counts as healthy, so a host whose table holds only such rows exits 0 with nothing printed, though no row was judged (`-x SMART` on a host with nothing mounted is the same). 1.65 says `Nothing was checked` only when no data row is left or no checked column is shown; 1.64 did the same here. The README's Health check section says so.
- Why: `check_rows()` calls a row healthy when it has no problem and no unknown, and a blank SMART is healthy by design (`SMART_HEALTHY`: a virtual device has none). Plan for 1.66: a row counts as judged only when one of its checked cells holds a value; a run with rows but none judged exits 3 with the "Nothing was checked" line. A host with real disks and virtual devices still exits 0 as now (its disks are judged); the lesson of 2026-11-23 then says that a check is healthy only when it judged a value.
- Revisit when: 1.66.
