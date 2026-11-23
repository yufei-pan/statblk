# statblk

Gather disk and partition information for block devices and print it as a table or JSON.

Supports **Linux** and **macOS**.

## Install

From PyPI:

```bash
pip install statblk
```

From a clone of this repository:

```bash
pip install .
```

Optional shell tab completion:

```bash
pip install 'statblk[completion]'
```

Requires **Python 3.6+**. statblk carries a copy of [multiCMD](https://pypi.org/project/multiCMD/) (1.69): an installed multiCMD is used when it is at least as new, the copy otherwise.

## Quick start

```bash
statblk
statblk -j                    # JSON output (rows, header first)
statblk -J                    # JSON objects with numeric sizes/rates
statblk -o NAME,SIZE,MOUNTPOINT
statblk sda nvme              # filter rows matching sda or nvme
statblk 2                     # refresh every 2 seconds (watch mode)
```

## Output columns

By default every column that has data is shown (a column that is empty for every row, such as `LABEL` when nothing is labelled, is hidden from the table):

| Column | Description |
|--------|-------------|
| `NAME` | Block device name (device-mapper devices show their `/dev/mapper` name, e.g. `pve-root`) |
| `FSTYPE` | Filesystem type |
| `SIZE` | Device or filesystem size |
| `FSUSE%` | Filesystem space used (mounted entries); `TIMEOUT` for a mount that didn't answer (e.g. dead NFS server), `ERROR` for one whose `statvfs` failed (e.g. `EIO`, a directory you cannot search): both have no `SIZE` |
| `MOUNTPOINT` | Mount path |
| `SMART` | SMART health: `OK`, `STANDBY` (spun-down drive, not woken), a failure such as `FAILED!`, `TIMEOUT` (smartctl stuck, or an earlier one on the disk still is), or why it couldn't be read (`NO SMARTCTL`, `DENIED`, `UNKNOWN`). Blank for devices without SMART (loop, dm, md, zram, nbd) |
| `LABEL` | Volume label |
| `UUID` | Filesystem UUID |
| `MODEL` | Drive model (from udev via `lsblk`, sysfs fallback) |
| `SERIAL` | Drive serial (from udev via `lsblk`, sysfs fallback) |
| `DISCARD` | TRIM / discard support |
| `READ` | Read throughput: the device's since-boot average on the first query, the live rate on later watch refreshes (see [READ / WRITE numbers](#read--write-numbers)) |
| `WRITE` | Write throughput, same as `READ` |

Use `-o` / `--output` to select columns (comma-separated) or `-x` / `--exclude` to omit columns. Columns named with `-o` are always shown, even when empty; `--show_empty_columns` keeps empty columns in the default view. JSON output (`-j` / `-J`) always includes every selected column.

### READ / WRITE numbers

The first query (a single run, or the first refresh of watch mode) does **not** show a real-time rate. It shows each device's **average since boot**: bytes read (or written) since boot divided by the time the kernel spent on reads (or writes) since boot. Idle time is left out, so the number describes the device's work pattern, how fast it typically moves data when it is working, rather than what it is doing at this moment. For example:

- a parity drive that mostly does long sequential syncs and scrubs shows a high READ (e.g. 150 MiB/s) even while it sits idle;
- a snap or disk image written once at install time can show a very high WRITE (e.g. 1 GiB/s), because all of its writes happened in one short burst;
- a device with no I/O since boot shows `0 B/s`, so `-A` on a single run lists the devices that have done any I/O since boot.

The kernel counts the time of every request separately, so a device with many requests in flight at once (e.g. NVMe under load) reports more busy time than wall-clock time, and its average reads lower than its real transfer speed.

From the second watch refresh on, READ / WRITE are **live rates**: bytes transferred during the last interval divided by the wall-clock time of that interval. `-J` gives the same values as bytes per second. READ / WRITE are blank (`null` in `-J`) where statblk has none to read: on macOS, for a device whose `stat` cannot be read, and for one refresh after a counter went back (the device was removed and added again under its name, or the counter wrapped).

## Options

### Output format

| Flag | Description |
|------|-------------|
| `-j`, `--json` | Print JSON instead of a table (list of rows, header first; values as displayed) |
| `-J`, `--json_objects` | Print JSON as a list of objects: `SIZE`/`READ`/`WRITE` in bytes and `FSUSE%` as an integer (`null` when unavailable) |
| `-b`, `--bytes` | Print sizes and throughput as raw byte counts |
| `-H`, `--si` | Use powers of 1000 (SI) instead of 1024 for sizes |
| `-R`, `--full` | Do not truncate long values to terminal width |
| `-o`, `--output` | Columns to include (default: all with data) |
| `-x`, `--exclude` | Columns to omit |
| `--show_empty_columns` | Keep columns that are empty for every row in the table |

### Filtering

| Flag | Description |
|------|-------------|
| `filter_patterns …` | Show rows matching any pattern (regex) |
| `-D`, `--match_devname_only` | Apply patterns to device names only (kernel name or `/dev/mapper` name) |
| `-v`, `--invert_match` | Invert pattern match (with no patterns, prints only the header; `--check` then checks nothing and exits `3`) |
| `-F`, `-fo`, `--formated_only` | Only entries with a filesystem type (one whose type could not be read stays, `FSTYPE` blank) |
| `-M`, `-mo`, `--mounted_only` | Only mounted devices |
| `-B`, `-bo`, `--best_only` | Shortest mount point per device |
| `-A`, `-ao`, `--active_only` | Only devices with read/write activity (since boot on the first query, during the last interval on later watch refreshes); a row with no throughput to read stays (every row on macOS, a `-P` filesystem), and so does a mount whose `FSUSE%` is `ERROR` or `TIMEOUT` |
| `-P`, `--pseudo` | Include pseudo filesystems (tmpfs, nfs, cifs, …) |
| `--show_zero_size_devices` | Include zero-size devices |
| `--show_squashfs` | Include squashfs images on loop devices (snaps, AppImages), hidden by default |

### Runtime

| Flag | Description |
|------|-------------|
| `-t`, `--timeout` | Time budget per refresh in seconds for `lsblk`, `smartctl` and `statvfs`; on macOS, how long `diskutil` and `mount` may each go without output (default: 2; fractions allowed; 0: no limit). A command it stops (`lsblk`, `diskutil`, `mount`) is named on stderr, with what it leaves missing, and so is one that is not found or fails (with `--check`, only when the run exits `1` or `3`) |
| `-w`, `--watch SECONDS` | Repeat output every SECONDS (watch mode; fractions allowed, e.g. `0.5`) |
| `--check` | Health check: print only the rows that need attention (exit 1 problem, 3 unknown), or print nothing (`-j`: the header row, `-J`: `[]`) and exit 0 (see [Health check](#health-check)) |
| `--max_use PCT` | FSUSE% at or above which `--check` reports a filesystem (default: 90) |
| `--sudo` | Run external commands via `sudo` (needed for SMART on many systems). `smartctl` is also looked up in `/usr/sbin`, `/sbin`, `/usr/local/sbin` when it isn't on `PATH` |
| `--debug` | Print suppressed exceptions to stderr |
| `-V`, `--version` | Show version and exit |

### Watch mode

Prefer `-w` / `--watch`, which also takes fractions. A trailing integer positional still works the same as before (whole seconds only, so a pattern like `0.5` stays a filter):

```bash
statblk -w 5       # update every 5 seconds
statblk -w 0.5     # twice a second
statblk 5          # same (trailing integer)
statblk sda 3      # filter to sda, refresh every 3 seconds
statblk -w 3 sda   # same with explicit flag (flag wins if both are given)
```

Each table refresh starts with a `watch(1)`-style header, `Every 2s on <hostname>: <date time>`. On a terminal the screen is redrawn in place; when output is piped or redirected every refresh is kept, so the log reads top to bottom. With `-j` / `-J`, watch mode prints one compact JSON document per line (NDJSON) so a reader can parse each refresh as it arrives; single-run JSON stays indented.

The first table shows each device's since-boot READ / WRITE average and later refreshes show live rates (see [READ / WRITE numbers](#read--write-numbers)). After the first refresh, `--active_only` is enabled automatically so only busy devices are shown (with the rows it keeps anyway: every row on macOS, the `-P` filesystems, a mount whose `FSUSE%` is `ERROR` or `TIMEOUT`), unless you gave filter patterns: devices you named stay on screen even while idle. Each refresh re-reads mounts, labels, UUIDs, sizes, and per-drive sysfs info such as model/serial, so hot-swapped drives show up correctly (throughput iterators stay live across refreshes). Press Ctrl-C to stop (exit status 130).

If a filter pattern looks like a number, append `0` so it is not treated as the refresh interval (or use `-w` and keep the number as a filter):

```bash
statblk nvme0 0    # match nvme0, single run (no watch)
statblk -w 0 nvme0 # same via flag
```

### Health check

`--check` runs once and prints only the rows that need attention; when everything is healthy it prints nothing (with `-j`, the header row alone; with `-J`, `[]`; as in 1.61), so cron only mails on trouble. Exit status:

| Exit | Meaning |
|------|---------|
| `0` | Healthy (no rows printed). A `STANDBY` drive counts as healthy: it is checked on the next run that finds it awake |
| `1` | Problem: `FSUSE%` at or above `--max_use` (default 90) or `TIMEOUT` (hung mount), or `SMART` reporting a failure — `FAILED!`, a vendor failure string, or `TIMEOUT` (smartctl stuck on the disk) |
| `3` | Unknown: no problem found, but SMART couldn't be read on a disk — `NO SMARTCTL` (install smartmontools), `DENIED` (run as root or with `--sudo`) or `UNKNOWN` (no verdict, e.g. a disk behind a RAID controller) — or a mount's `FSUSE%` is `ERROR` (its disk's SMART still counts: a failing one is a problem), or a command that can hide what the check reads did not answer in full (see below), or nothing could be checked: `-x` leaves out both `FSUSE%` and `SMART`, or `-v` has no pattern (said on stderr) |

A problem beats an unknown, and both kinds of rows are listed. A command that did not answer in full (stopped by `--timeout`, not found, or failed) counts only when the check depends on it: `mount` on macOS (FSUSE%, and with `-M` which disks are mounted: the disks it did not list are missing from the table too), or any command when a pattern (not `-D`) filters the rows (`lsblk` only when FSTYPE, UUID, MODEL or SERIAL is collected). It is named on stderr, after the rows, only when the run exits `1` or `3`. Exit `3` exists so that "not checked" never looks like "healthy" in a sweep. For a space-only check use `-x SMART`; to skip a device that has no SMART at all (an SD card, a USB stick) filter it out, e.g. `statblk --check -D -v mmcblk`. `FSUSE%` and `SMART` are always added to the shown columns so you can see why a row failed; excluding one with `-x` turns that check off, and excluding both leaves nothing to check (exit `3`). Filters (`-F`, `-M`, `-B`, `-v` and patterns) and JSON output (`-j` / `-J`) work as usual, but filters narrow what is checked: `-M` skips disks with no mount of their own (md/LVM/ZFS/Ceph members, extra btrfs pool devices), a pattern skips a disk none of whose rows it matches, and `-F` skips a disk with no filesystem type (the Mac's own SSD, say), so cluster sweeps should run plain `--check`. A whole disk that reports a size of zero and has no partition row to show is hidden, and so not checked, unless `--show_zero_size_devices` (a known limitation, [docs/limitations.md](docs/limitations.md)). `--check` can't be combined with watch mode.

In every mode, Ctrl-C exits `130`, and when the reader closes the pipe before statblk has written everything (`statblk -w 2 | head`) the run ends quietly with `141` (128 + SIGPIPE).

```bash
statblk --check || mail -s "disk alert on $(hostname)" ops@example.com   # cron
statblk --check -x SMART --max_use 80                                    # space only
mssh 'nodes[1-64]' 'statblk --check'                                     # whole cluster via multiSSH3
```

## Platform notes

### Linux

Uses sysfs, `/proc/self/mountinfo`, `lsblk`, and optionally `smartctl`.

- **SMART** requires `smartctl` (smartmontools). Use `--sudo` if permission is denied. It only runs against hardware-backed disks (not loop, dm, md, zram, nbd). smartctl runs with `-n standby`, so spun-down drives are not woken (not even by watch mode); they show `STANDBY` until they're next awake. This is verified for SATA drives on the kernel's libata driver; drives behind USB enclosures or some RAID/SAS controllers may still spin up, because smartctl's device-type probe goes through the bridge. On a hardware disk where SMART can't be read the column says why (`NO SMARTCTL`, `DENIED`, `UNKNOWN`); it is blank for virtual devices. A smartctl stuck in uninterruptible I/O on a dying disk can't be killed and outlives the refresh (and statblk); while one older than `--timeout` is still running on a disk, statblk starts no new one and shows `TIMEOUT` for that disk at once, so `-w` and repeated runs leave at most one per disk (a few for a disk hidden by `-M` or a `-D` filter, which statblk never waits on). With `--timeout 0` this check is off. It sees only processes in statblk's own `/proc`: with `hidepid` as a non-root user (`--sudo`), or in a fresh container, it can't see an earlier stuck smartctl, so run statblk as root on the host, or in hidepid's `gid=` group ([docs/limitations.md](docs/limitations.md)).
- **squashfs on loop devices** (snap packages, AppImages) is hidden by default: these images are read-only and always 100% full. Use `--show_squashfs` to list them. Other loop devices, such as a mounted disk image, are always shown.
- **autofs** trigger mounts are ignored (stat-ing them would trigger the automount); the real filesystem appears once mounted.
- **READ / WRITE** come from `/sys/class/block/*/stat` (always 512-byte sector units): a since-boot average on the first query, live rates on later watch refreshes (see [READ / WRITE numbers](#read--write-numbers)).

### macOS

Uses `diskutil` and `mount`, found in `/usr/sbin` and `/sbin` too when `PATH` lacks them (cron's does). READ and WRITE are blank (`null` in `-J`): macOS has no per-device throughput to read, so `-A` filters nothing. APFS snapshot nodes such as the sealed system volume (`disk3s1s1` on `/`) are listed. Every device is listed, mounted or not, except one whose size reads 0 (shown with `--show_zero_size_devices`). `DISCARD` is `diskutil`'s `Solid State`.

## Upgrading to 1.65 from 1.64

- `--check` exits 3, with a line on stderr (`Nothing was checked: ...`), when it is left nothing to judge: `-x` leaves out both `FSUSE%` and `SMART` (or no valid `-o` column is left), or `-v` has no pattern. 1.64 printed nothing and exited 0. `-j` and `-J` print what they print for a healthy run.
- In watch mode, READ or WRITE is blank (`null` in `-J`) for one refresh after the device's counter went back (the device was removed and added again under its name, or the counter wrapped), where 1.64 showed a negative rate.
- `statblk -w 2 2>>log` on a terminal writes a command's note (stopped, not found or failed) to the log once per run, where 1.64 wrote it on every refresh. With stderr on the terminal too, the note still follows each redrawn table.
- `-o ALL` (any case) means every column, as `-o all` does; 1.64 read it as an unknown column and printed an empty table.
- The embedded multiCMD is now 1.69. Nothing statblk shows changes.
- Library callers: `get_read_write_rate_throughput_iter()` yields None for a direction whose counter went back.

## Upgrading to 1.64 from 1.63

- A command that is not found or fails is now named on stderr, with what it leaves missing, and counts in `--check` as one `--timeout` stopped does (1.63 counted only a stop): `lsblk` on Linux, `diskutil` and `mount` on macOS. A healthy `--check` that 1.63 passed with exit 0 can now exit 3: on macOS when `mount` fails (FSUSE% was not read), and with a pattern (not `-D`) when `lsblk` or `diskutil` is missing or fails. With `--sudo`, a missing `lsblk` reads `lsblk failed (exit 1)`, sudo's own status. The "lsblk not found" note now also shows with `-F` and when no row is left.
- macOS: `diskutil` and `mount` are also looked up in `/usr/sbin` and `/sbin`, which cron's `PATH` (`/usr/bin:/bin`) lacks. Under cron, 1.63 found neither: no SIZE, FSTYPE, UUID or LABEL from `diskutil`, no mounted filesystem, and `--check` read no FSUSE%.
- macOS: FSTYPE is the word `mount` prints (`apfs`, `msdos`, `exfat`, `hfs`) for unmounted volumes too, where 1.63 showed `diskutil`'s `APFS` or `MS-DOS FAT32`, so a pattern matches mounted and unmounted volumes alike. READ and WRITE are blank (`null` in `-J`), not a `0 B/s` statblk never measured, so the default table hides them.
- `-F`, `-A` and the size filters no longer drop a row on a value statblk could not read: on Linux a sysfs size or stat that cannot be read (a device that vanished mid-run) leaves SIZE, or READ and WRITE, blank (`null` in `-J`). `-A` keeps the `-P` rows on Linux, and `-A` (so watch mode after its first refresh) keeps a mount whose FSUSE% is `ERROR` or `TIMEOUT`. A failing disk 1.63 hid this way is reported by `--check` (exit 1).
- On Linux a hidden NVMe multipath path node (`nvme3c3n1`: no device number, no `/dev` node, and its namespace `nvme3n1` is the same disk) is no longer a row, as `lsblk` does not list it.
- Mount points: on macOS a `-P` share whose source has a space is listed, and a volume whose mount point holds " (" gets its FSUSE% (1.63: `ERROR`, so `--check` exited 3); on Linux so does a mount point that is not UTF-8, or not ASCII under Python 3.6 in the C locale (EL8's). An SMB or CIFS source shows as `//server/share` (1.63: `/server/share`).
- The embedded multiCMD is now 1.68. On a terminal that reports no size (0 columns: `script` with no terminal of its own, some CI runners) the table fits 80 columns, or `COLUMNS`; 1.63 cut every column to its heading's width there. Through a pipe nothing changes.
- Library callers: `get_drives_info()` takes `unanswered=`, a dict that gets each command that did not answer in full with its return code (124 stopped, 127 not found, other failed); `cut=` still gets the stopped ones. `parseMount()` takes `unanswered=` in place of `cut=`, `get_macos_diskutil_info()` in place of `cut=` and `failed=`, `find_smartctl()` is `find_command(name)`, `SMARTCTL_FALLBACK_DIRS` is `SBIN_DIRS`, and `LSBLK_MISSING_NOTE` is gone.

## Upgrading to 1.63 from 1.62

- macOS: every device is listed, mounted or not (except one whose size reads 0), with the SIZE and FSTYPE of an unmounted device, and the UUID, LABEL and DISCARD, from `diskutil`. On macOS 26, 1.62 read only the first of the sections `diskutil info -all` prints for each device, so a disk with no mounted filesystem (such as the internal SSD's `disk0`) was not listed, and `--check` did not see its SMART. `--check` now judges it: one whose SMART cannot be read (an unmounted USB disk, a disk image) exits 3 where 1.62 did not list it.
- A row is no longer dropped on a value statblk could not read (not run, stopped or failed), except `-M` with a stopped `mount` (the disks it did not list go, and stderr says so) and the cases in [docs/limitations.md](docs/limitations.md), where a source that failed without being stopped, or a size that reads 0, still hides a row. On macOS a device `diskutil` gave no size is listed with SIZE blank (a size of 0 still hides it), and `-A` filters nothing (1.62 listed no device). `-F` keeps a device whose filesystem type could not be read (no `lsblk`, a stopped or failed `lsblk` or `diskutil`, a stopped `mount`), with FSTYPE blank. A mount whose `statvfs` fails (`EIO`, a directory you cannot search) is listed with SIZE blank and FSUSE% `ERROR` (`-J`: `null`), where 1.62 dropped it as a size of 0.
- `--check` exit codes: a failing disk 1.62 hid that way is reported (exit 1, where 1.62 gave 0 or 3). A mount with FSUSE% `ERROR` exits 3, or 1 when its disk's SMART fails. A stopped `diskutil`, or a stopped `lsblk` with `-F`, no longer turns a healthy run unknown: it exits 0 and prints nothing, where 1.62 exited 3. A stopped `mount` on macOS, and any stopped command with a pattern (not `-D`), still count as before.
- On macOS the LABEL and UUID, and the FSTYPE of an unmounted device, now come from `diskutil`, so a pattern matches more text than in 1.62: it can keep rows 1.62 dropped, and `-v` can drop rows 1.62 kept.
- The stderr notes for a stopped `diskutil` and for a missing or stopped `lsblk` say what is left blank.

## Upgrading to 1.62 from 1.61

- The embedded multiCMD is now 1.67. It runs whenever the installed multiCMD is older than 1.67, missing, or fails to import. Nothing statblk shows changes.
- A command `--timeout` stopped is now named on stderr, after the table or JSON and once per run in `-w` (under each table when it is redrawn on a terminal): `lsblk` (Linux, when FSTYPE, UUID, MODEL or SERIAL is shown, or `-F` needs FSTYPE), `diskutil` or `mount` (macOS), with what it leaves missing. 1.61 said nothing. In `--check`, one that can hide what the check reads makes a run with no problem exit 3, where 1.61 exited 0 ([Health check](#health-check) says which); a healthy run exits and prints as in 1.61, and a run that exits 1 or 3 also names each stopped command.
- On Python 3.6 (EL7, EL8), a Ctrl-C that landed just as statblk started a filesystem's statvfs thread could hang `statblk -w` for good. It now exits 130.
- pip no longer installs multiCMD for statblk. With pip 9 (EL7, EL8) and multiCMD 1.57 or older installed, `pip3 install -U statblk` stopped with `configparser.DuplicateOptionError`. A multiCMD installed only for statblk can stay or go.

## Upgrading to 1.61 from 1.60

- On macOS, `-t 0` now gives `diskutil` and `mount` no limit, as it already did for `smartctl` and `statvfs`. Before, `diskutil` got 4 s and `mount` 1 s, so a slow one left SIZE, FSTYPE, MOUNTPOINT and other columns blank.
- On macOS, a non-zero `-t` now limits `mount` too. It gets `--timeout` (2 s by default), where it always got 1 s. `diskutil` gets `--timeout`, as before. Both limits count time without output.
- Library callers: `get_drives_info()` with no `timeout` now waits without limit for every command. In 1.60 it printed a `TypeError` traceback and left the lsblk columns blank on Linux, and on macOS gave `diskutil` 4 s and `mount` 1 s.
- The embedded multiCMD is now 1.61. It runs whenever the installed multiCMD is older than 1.61, so multiCMD itself need not be upgraded.
- On Python 3.6 to 3.10, a Ctrl-C that stops a command just as it starts no longer crashes the Python that starts it. On 3.6 and 3.7 that crash left a core dump, which abrt or systemd-coredump then reported.
- On Python 3.6 to 3.10, a Ctrl-C while `diskutil` or `mount` starts on macOS no longer leaves that command running after statblk ends.
- A first Ctrl-C that lands in the few milliseconds when statblk starts `lsblk` or `smartctl` is now dropped a little more often (about 1 in 700 of those, against 1 in 1,400). Python prints "Exception ignored". Press Ctrl-C again.

## Upgrading to 1.60 from 1.59

- `-t 0` now waits for `lsblk` with no limit, as it already did for `smartctl`. Before, it did not wait at all, so a slow `lsblk` could leave SERIAL and other `lsblk` columns blank. With a limit, `lsblk` now gets what is left of the refresh's `--timeout`, not a fresh `--timeout` of its own.
- The embedded multiCMD is now 1.58: no change to how commands run. The embedded copy also runs when the installed multiCMD fails to import in any way, not only when it is older or missing. multiCMD itself need not be upgraded.

## Upgrading to 1.59 from 1.58

- The embedded multiCMD is now 1.57. It runs whenever the installed multiCMD is older, so multiCMD itself need not be upgraded.
- Faster command starts on Python 3.6 - 3.10, where the embedded multiCMD 1.57 imports only built-in modules in the wrapper that puts each command in its own process group (about 7 ms to 3.5 ms of CPU per command on Python 3.6.8). Nothing else about starting a command changes.

## Upgrading to 1.58 from 1.57

- On Linux, a disk whose earlier smartctl is still stuck (older than `--timeout`, from a previous refresh, run, cron job or another tool) now shows `TIMEOUT` at once and gets no new smartctl. `statblk -w` and repeated runs leave at most one stuck smartctl per disk instead of one per refresh (a few for a disk hidden by `-M` or a `-D` filter, which statblk never waits on), and the refresh no longer waits out `--timeout` for that disk. macOS and `--timeout 0` are unchanged.

## Upgrading to 1.57 from 1.56

- multiCMD 1.56 or newer is required (the embedded copy is 1.56).
- With no `lsblk` installed, the "lsblk not found" note now goes to stderr after the table, not before it: once per run, and under every table while `-w` redraws a terminal, so it no longer vanishes at once. It also shows with `--sudo` now.
- A reader that closes the pipe early (`statblk | head`) now ends the run with exit status 141 (128 + SIGPIPE), not 1, so it can't be mistaken for `--check`'s "problem".
- `--debug` no longer prints the "smartctl not found" hint; the SMART column already says `NO SMARTCTL`.
- Library callers: `get_drives_info` no longer prints the lsblk note, and `cache_decorator`, `clear_caches` and `debug_msg` are gone.

## Development

Install test deps:

```bash
pip install -r requirements-dev.txt
```

Run unit tests (default; live excluded) and embedded doctests:

```bash
pytest
python -m doctest statblk.py -v
python statblk.py --doctest
```

Optional live checks:

```bash
pytest -m live          # soft smoke on this host
pytest -m live_strict   # compare FSUSE% and names to df/lsblk
```

## License

GPLv3+ — Yufei Pan ([pan@zopyr.us](mailto:pan@zopyr.us))

Project home: [github.com/yufei-pan/statblk](https://github.com/yufei-pan/statblk)
