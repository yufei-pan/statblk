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
- What the operator sees: statblk hides a device whose size reads 0 (an empty card-reader slot, empty virtual media) unless `--show_zero_size_devices`. A partition row carries its parent's SMART, so a failing disk is still judged through any partition row that is shown; a whole disk of size 0 with no partition row shown goes unjudged by a plain `statblk --check` (exit 0, nothing printed). `statblk --check --show_zero_size_devices` judges it. On Linux, with `lsblk` stopped or missing, a size that cannot be read counts as 0 too (the deferred entry "Linux: an unreadable sysfs size or stat reads as 0", below).
- Why: the zero-size rule keeps an empty slot from showing as a disk, and `--check` judges the rows the table shows. Reproduced with fake commands only, not on a real disk; 1.62 and 1.61 did the same.
- Revisit when: someone sees it on a real disk, or measures what smartctl answers for one.
- Approved: 2026-11-16, chief's decision C78 (the user's desk session; not the user's words): option (1), a known limitation with one README line.

### A command that failed without being stopped is not recorded (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: the cut rule and the stderr note count only a command `--timeout` stopped (for `lsblk`, also one still running at the deadline). An `lsblk` that is missing (it has its own note, which the rule does not read) or exits with an error, a macOS `diskutil` that exits with an error and prints nothing, and a macOS `mount` that fails (non-zero exit, or nothing printed), do not count. So `statblk --check PATTERN` on a Linux host with no working `lsblk`, with a failing disk whose unmounted filesystem the pattern matches only through `lsblk`'s FSTYPE, exits 0 and prints nothing, and a pattern that only a failed `diskutil` would have filled does the same on macOS. A macOS `mount` that fails leaves every device listed with MOUNTPOINT and FSUSE% blank (1.62 listed no device), with no note, so `--check` exits 0 over a full filesystem, and with `-M`, which drops the rows `mount` did not list, over a failing disk. 1.62 exited 0 in each of these runs.
- Why: `cut` is filled for return code 124 (and a still-running `lsblk`) only; a missing `lsblk` is found by `shutil.which` in `main()`; 1.63's `diskutil` `failed` list is one more such record.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): one record of "did not answer in full" per command (stopped, missing or failed), read by the pattern term of the cut rule and by the stderr note; `main()`'s `shutil.which('lsblk')` and the `failed` list go. `-F` keeps a device whose type a failed command did not give, as 1.63 does. The cost to weigh: on a host with no `lsblk`, a healthy `statblk --check sda` would then exit 3 until the operator writes `-D sda`.

### `-F` with no `lsblk` does not say why it filters nothing (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: with no `lsblk`, `statblk -F -o NAME,SIZE` lists sda, sda1, sdb and sdb1, because the type of an unmounted device was not read (1.62 listed only the mounted sda1), and stderr is empty (1.62's too). The "lsblk not found" note is printed only when FSTYPE, UUID, MODEL or SERIAL is shown, and `-F` needs FSTYPE without showing it.
- Why: `note_due` in `main()` looks at the shown columns only, and `-F` needs FSTYPE without showing it.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): `note_due` also holds when `-F` is given (`... and (args.formated_only or LSBLK_NOTE_FIELDS.intersection(results[0]))`), with a test.

### macOS: FSTYPE reads `APFS` on an unmounted volume and `apfs` on a mounted one (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: `statblk` shows `apfs` (from `mount`) for disk3s5 and `APFS` (diskutil's File System Personality) for the unmounted disk3s3, so `statblk apfs` lists only the mounted volumes and `statblk APFS` only the unmounted ones. New to see in 1.63, because 1.62 listed no unmounted volume.
- Why: `get_macos_diskutil_info()` takes FSTYPE from File System Personality.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): take FSTYPE from `Type (Bundle)` (all 13 volumes of the test capture have it, and it is the word `mount` prints), falling back to File System Personality; with a test on the capture.

### macOS: a `Volume Total Space` line overrides a size of 0 (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: a device with `Disk Size: 0 B` and a `Volume Total Space` line gets the volume's size and is listed, where the rule says a size of 0 hides it. 1.62 did the same, for a `Volume Total Space` line in the first section of the device that it read. The test capture (macOS 26) has no `Volume Total Space` line, so this can only show on another macOS, and the fallback itself has no test.
- Why: `get_macos_diskutil_info()` treats a parsed 0 as "no size yet" (`if not size_bytes ...`).
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): `if size_bytes is None ...`, with two cases in `test_diskutil_size_none_when_it_gave_none` (only `Volume Total Space`; `Disk Size` 0 plus `Volume Total Space`), or drop the fallback if no macOS that prints it can be named.

### Linux: `-F` drops a partition that `lsblk` answered without (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: `lsblk` exits 0 but does not list a device (a partition that appeared after it ran, or a name it prints differently): `-F` drops that device's row for a blank FSTYPE that was never read, and `--check -F` does not judge its disk through it. 1.62 did the same.
- Why: "answered in full" is one flag for the whole `lsblk` output on Linux; macOS asks per device (`device_name in macos_info`).
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): a per-device answer on Linux too (`device_name in` what `lsblk` listed), with a test.

### Linux: an unreadable sysfs size or stat reads as 0 (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: with `lsblk` stopped or missing, a sysfs `size` that cannot be read (a device that vanished between the listing and the read) reads as 0 and drops the row; `-A` drops a device whose sysfs `stat` cannot be read as idle. A failing disk that is only that row exits 0. A race, so rare. 1.62 did the same.
- Why: `read_int()` returns 0 on any failure, and the throughput iterator yields `0, 0`.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): both give None for "not read", as macOS's size does, and the filters drop only a value that was read; with tests that force the failure.

### Linux: `-A` drops the `-P` pseudo rows (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: `statblk -A -P` drops every pseudo filesystem row (tmpfs, nfs...) because they have no throughput iterator, while macOS keeps them. 1.62 did the same.
- Why: the `-A` test is `device_name not in tptDict`, true for a mount that is no block device.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): `-A` filters only devices that have a throughput to read.

### Watch mode: `-A` hides a device's `ERROR` or `TIMEOUT` mount row after the first refresh (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: `statblk -w SECONDS` with no pattern switches `-A` on after its first refresh, so a mount of an idle device whose `statvfs` fails (`ERROR`) or hangs (`TIMEOUT`) is shown once and then gone, and so are all the `-P` rows (the entry above). The comment in `get_drives_info()` says such a row is always shown; it is, on the first refresh only. A hang did the same in 1.62; `ERROR` is new in 1.63 (1.62 dropped the row as a size of 0). Run with a block device whose mount gives a `PermissionError`, and with a faked hang.
- Why: the idle test of `-A` is applied before a device's mounts are read, so a mount that fails or hangs never gets to show it.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): a mount row that failed (`ERROR` or `TIMEOUT`) passes the active filter, as the comment says, and the `-P` rows with it; this reads `statvfs` for an idle device's mounts on every refresh.

### macOS: a mount line with a space in its source, or " (" in its mount point, is misread (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: with `-P`, a network mount whose source has a space (`//user@server/My Share on /Volumes/My Share (smbfs, ...)`) never becomes a row. A volume whose name has " (" in it (`/Volumes/Backup (old)`) is read at a cut-short mount point, so its statvfs fails: FSUSE% `ERROR`, and a healthy `--check` exits 3 (1.62 left the volume out of the table and its space unchecked, exit 0). Seen with a faked `mount` line (macOS `mount(8)`'s format), not on a Mac.
- Why: `parse_darwin_mount_line()` reads the source as one word (`\S+`) and the mount point up to the first " (".
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): read the source up to ` on ` and the options from the last parenthesis (`^(.+?)\s+on\s+(.+)\s+\(([^()]*)\)$`), with a test on each line. On Linux, read mountinfo with `errors='surrogateescape'`, so a non-UTF-8 mount path reaches statvfs intact.

### macOS: READ and WRITE show `0 B/s` that was never read (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: READ and WRITE on macOS read `0 B/s` for every device, a number statblk did not measure, and `-J` gives 0 for it.
- Why: the throughput iterator yields `0, 0` on macOS. 1.63 makes `-A` filter nothing there, where 1.62's `-A` dropped every row, since every device read `0 B/s`.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): blank cells (`null` in `-J`) on macOS, so the table says what it did not read.

### The macOS test of a silent `diskutil` and `mount` has a thin time margin (deferred, 1.64)
- Kind: deferred (1.64)
- What the operator sees: nothing; on the test Mac `test_a_silent_diskutil_and_mount_are_stopped_and_recorded` failed once on a first run (and passed in 19 further runs), because it gives the fake commands 0.3 s to print a first line, and a fresh script there takes 0.09 to 0.12 s to print it. The cause is likely, not proven: the measured latency explains a margin of 3x, not the one run over 0.3 s.
- Why: the comment in the test says 15 times what the test needs, which holds on Linux (0.02 s measured) and not on the Mac.
- Revisit when: statblk 1.64, started right after 1.63.
- Plan (1.64): a test-only fix with a margin measured on the Mac, and the comment corrected.
