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

Requires **Python 3.6+** and the [multiCMD](https://pypi.org/project/multiCMD/) package (>= 1.47).

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
| `FSUSE%` | Filesystem space used (mounted entries); `TIMEOUT` for a mount that didn't answer (e.g. dead NFS server) |
| `MOUNTPOINT` | Mount path |
| `SMART` | SMART health: `OK`, `STANDBY` (spun-down drive, not woken), a failure such as `FAILED!`, `TIMEOUT` (smartctl stuck), or why it couldn't be read (`NO SMARTCTL`, `DENIED`, `UNKNOWN`). Blank for devices without SMART (loop, dm, md, zram, nbd) |
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

From the second watch refresh on, READ / WRITE are **live rates**: bytes transferred during the last interval divided by the wall-clock time of that interval. `-J` gives the same values as bytes per second.

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
| `-v`, `--invert_match` | Invert pattern match (with no patterns, prints only the header) |
| `-F`, `-fo`, `--formated_only` | Only entries with a filesystem type |
| `-M`, `-mo`, `--mounted_only` | Only mounted devices |
| `-B`, `-bo`, `--best_only` | Shortest mount point per device |
| `-A`, `-ao`, `--active_only` | Only devices with read/write activity (since boot on the first query, during the last interval on later watch refreshes) |
| `-P`, `--pseudo` | Include pseudo filesystems (tmpfs, nfs, cifs, …) |
| `--show_zero_size_devices` | Include zero-size devices |
| `--show_squashfs` | Include squashfs images on loop devices (snaps, AppImages), hidden by default |

### Runtime

| Flag | Description |
|------|-------------|
| `-t`, `--timeout` | Time budget per refresh in seconds for `lsblk`, `smartctl` and `statvfs` (default: 2; fractions allowed) |
| `-w`, `--watch SECONDS` | Repeat output every SECONDS (watch mode; fractions allowed, e.g. `0.5`) |
| `--check` | Health check: print only problem rows and exit 1, or print nothing and exit 0 (see [Health check](#health-check)) |
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

The first table shows each device's since-boot READ / WRITE average and later refreshes show live rates (see [READ / WRITE numbers](#read--write-numbers)). After the first refresh, `--active_only` is enabled automatically on Linux so only busy devices are shown, unless you gave filter patterns: devices you named stay on screen even while idle (not on macOS, where throughput isn't available; `-A` still forces it). Each refresh re-reads mounts, labels, UUIDs, sizes, and per-drive sysfs info such as model/serial, so hot-swapped drives show up correctly (throughput iterators stay live across refreshes). Press Ctrl-C to stop (exit status 130).

If a filter pattern looks like a number, append `0` so it is not treated as the refresh interval (or use `-w` and keep the number as a filter):

```bash
statblk nvme0 0    # match nvme0, single run (no watch)
statblk -w 0 nvme0 # same via flag
```

### Health check

`--check` runs once and prints only the rows that need attention; when everything is healthy it prints nothing, so cron only mails on trouble. Exit status:

| Exit | Meaning |
|------|---------|
| `0` | Healthy (nothing printed). A `STANDBY` drive counts as healthy: it is checked on the next run that finds it awake |
| `1` | Problem: `FSUSE%` at or above `--max_use` (default 90) or `TIMEOUT` (hung mount), or `SMART` reporting a failure — `FAILED!`, a vendor failure string, or `TIMEOUT` (smartctl stuck on the disk) |
| `3` | Unknown: no problem found, but SMART couldn't be read on a disk — `NO SMARTCTL` (install smartmontools), `DENIED` (run as root or with `--sudo`) or `UNKNOWN` (no verdict, e.g. a disk behind a RAID controller) |

A problem beats an unknown, and both kinds of rows are listed. Exit `3` exists so that "not checked" never looks like "healthy" in a sweep. For a space-only check use `-x SMART`; to skip a device that has no SMART at all (an SD card, a USB stick) filter it out, e.g. `statblk --check -D -v mmcblk`. `FSUSE%` and `SMART` are always added to the shown columns so you can see why a row failed; excluding one with `-x` turns that check off. Filters (`-M`, `-B`, patterns) and JSON output (`-j` / `-J`) work as usual, but filters narrow what is checked: `-M` and patterns skip disks with no mount of their own (md/LVM/ZFS/Ceph members, extra btrfs pool devices), so cluster sweeps should run plain `--check`. `--check` can't be combined with watch mode.

```bash
statblk --check || mail -s "disk alert on $(hostname)" ops@example.com   # cron
statblk --check -x SMART --max_use 80                                    # space only
mssh 'nodes[1-64]' 'statblk --check'                                     # whole cluster via multiSSH3
```

## Platform notes

### Linux

Uses sysfs, `/proc/self/mountinfo`, `lsblk`, and optionally `smartctl`.

- **SMART** requires `smartctl` (smartmontools). Use `--sudo` if permission is denied. It only runs against hardware-backed disks (not loop, dm, md, zram, nbd). smartctl runs with `-n standby`, so spun-down drives are not woken (not even by watch mode); they show `STANDBY` until they're next awake. This is verified for SATA drives on the kernel's libata driver; drives behind USB enclosures or some RAID/SAS controllers may still spin up, because smartctl's device-type probe goes through the bridge. On a hardware disk where SMART can't be read the column says why (`NO SMARTCTL`, `DENIED`, `UNKNOWN`); it is blank for virtual devices.
- **squashfs on loop devices** (snap packages, AppImages) is hidden by default: these images are read-only and always 100% full. Use `--show_squashfs` to list them. Other loop devices, such as a mounted disk image, are always shown.
- **autofs** trigger mounts are ignored (stat-ing them would trigger the automount); the real filesystem appears once mounted.
- **READ / WRITE** come from `/sys/class/block/*/stat` (always 512-byte sector units): a since-boot average on the first query, live rates on later watch refreshes (see [READ / WRITE numbers](#read--write-numbers)).

### macOS

Uses `diskutil` and `mount`. Throughput columns are always zero (no per-device sysfs stats). APFS snapshot nodes such as the sealed system volume (`disk3s1s1` on `/`) are listed.

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
