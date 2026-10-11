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
| `SMART` | SMART health (`OK`, `DENIED`, `TIMEOUT`, etc.) |
| `LABEL` | Volume label |
| `UUID` | Filesystem UUID |
| `MODEL` | Drive model (from udev via `lsblk`, sysfs fallback) |
| `SERIAL` | Drive serial (from udev via `lsblk`, sysfs fallback) |
| `DISCARD` | TRIM / discard support |
| `READ` | Current read throughput |
| `WRITE` | Current write throughput |

Use `-o` / `--output` to select columns (comma-separated) or `-x` / `--exclude` to omit columns. Columns named with `-o` are always shown, even when empty; `--show_empty_columns` keeps empty columns in the default view. JSON output (`-j` / `-J`) always includes every selected column.

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
| `-A`, `-ao`, `--active_only` | Only devices with read/write activity |
| `-P`, `--pseudo` | Include pseudo filesystems (tmpfs, nfs, cifs, …) |
| `--show_zero_size_devices` | Include zero-size devices |
| `--show_squashfs` | Include squashfs images on loop devices (snaps, AppImages), hidden by default |

### Runtime

| Flag | Description |
|------|-------------|
| `-t`, `--timeout` | Time budget per refresh in seconds for `lsblk`, `smartctl` and `statvfs` (default: 2) |
| `-w`, `--watch SECONDS` | Repeat output every SECONDS (watch mode) |
| `--sudo` | Run external commands via `sudo` (needed for SMART on many systems). `smartctl` is also looked up in `/usr/sbin`, `/sbin`, `/usr/local/sbin` when it isn't on `PATH` |
| `--debug` | Print suppressed exceptions to stderr |
| `-V`, `--version` | Show version and exit |

### Watch mode

Prefer `-w` / `--watch`. A trailing integer positional still works the same as before:

```bash
statblk -w 5       # update every 5 seconds
statblk 5          # same (trailing integer)
statblk sda 3      # filter to sda, refresh every 3 seconds
statblk -w 3 sda   # same with explicit flag (flag wins if both are given)
```

After the first refresh, `--active_only` is enabled automatically on Linux so only busy devices are shown (not on macOS, where throughput isn't available). Each refresh re-reads mounts, labels, UUIDs, sizes, and per-drive sysfs info such as model/serial, so hot-swapped drives show up correctly (throughput iterators stay live across refreshes). Press Ctrl-C to stop (exit status 130).

If a filter pattern looks like a number, append `0` so it is not treated as the refresh interval (or use `-w` and keep the number as a filter):

```bash
statblk nvme0 0    # match nvme0, single run (no watch)
statblk -w 0 nvme0 # same via flag
```

## Platform notes

### Linux

Uses sysfs, `/proc/self/mountinfo`, `lsblk`, and optionally `smartctl`.

- **SMART** requires `smartctl` (smartmontools). Use `--sudo` if permission is denied. It only runs against hardware-backed disks (not loop, dm, md, zram, nbd). The column is hidden when no disk reports SMART; use `-o` or `--show_empty_columns` to show it and `--debug` to see why it is empty.
- **squashfs on loop devices** (snap packages, AppImages) is hidden by default: these images are read-only and always 100% full. Use `--show_squashfs` to list them. Other loop devices, such as a mounted disk image, are always shown.
- **autofs** trigger mounts are ignored (stat-ing them would trigger the automount); the real filesystem appears once mounted.
- **READ / WRITE** throughput comes from `/sys/class/block/*/stat` (always 512-byte sector units).
- On a single-shot run (and the first row of watch mode), READ/WRITE are a lifetime busy-time average (bytes / time spent in I/O since boot). In watch mode, later refreshes are interval rates over the sleep period (Δbytes / wall clock).

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
