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
statblk -j                    # JSON output
statblk -o NAME,SIZE,MOUNTPOINT
statblk sda nvme              # filter rows matching sda or nvme
statblk 2                     # refresh every 2 seconds (watch mode)
```

## Output columns

By default all columns are shown:

| Column | Description |
|--------|-------------|
| `NAME` | Block device name |
| `FSTYPE` | Filesystem type |
| `SIZE` | Device or filesystem size |
| `FSUSE%` | Filesystem space used (mounted entries) |
| `MOUNTPOINT` | Mount path |
| `SMART` | SMART health (`OK`, `DENIED`, etc.) |
| `LABEL` | Volume label |
| `UUID` | Filesystem UUID |
| `MODEL` | Drive model |
| `SERIAL` | Drive serial |
| `DISCARD` | TRIM / discard support |
| `READ` | Current read throughput |
| `WRITE` | Current write throughput |

Use `-o` / `--output` to select columns (comma-separated) or `-x` / `--exclude` to omit columns.

## Options

### Output format

| Flag | Description |
|------|-------------|
| `-j`, `--json` | Print JSON instead of a table |
| `-b`, `--bytes` | Print sizes and throughput as raw byte counts |
| `-H`, `--si` | Use powers of 1000 (SI) instead of 1024 for sizes |
| `-R`, `--full` | Do not truncate long values to terminal width |
| `-o`, `--output` | Columns to include (default: all) |
| `-x`, `--exclude` | Columns to omit |

### Filtering

| Flag | Description |
|------|-------------|
| `filter_patterns …` | Show rows matching any pattern (regex) |
| `-D`, `--match_devname_only` | Apply patterns to device names only |
| `-v`, `--invert_match` | Invert pattern match |
| `-F`, `-fo`, `--formated_only` | Only entries with a filesystem type |
| `-M`, `-mo`, `--mounted_only` | Only mounted devices |
| `-B`, `-bo`, `--best_only` | Shortest mount point per device |
| `-A`, `-ao`, `--active_only` | Only devices with read/write activity |
| `-P`, `--pseudo` | Include pseudo filesystems (tmpfs, nfs, cifs, …) |
| `--show_zero_size_devices` | Include zero-size devices |

### Runtime

| Flag | Description |
|------|-------------|
| `-t`, `--timeout` | Subprocess timeout in seconds (default: 2) |
| `--sudo` | Run external commands via `sudo` (needed for SMART on many systems) |
| `--debug` | Print suppressed exceptions to stderr |
| `-V`, `--version` | Show version and exit |

### Watch mode

Pass a refresh interval as the last positional argument (seconds):

```bash
statblk 5          # update every 5 seconds
statblk sda 3      # filter to sda, refresh every 3 seconds
```

After the first refresh, `--active_only` is enabled automatically so only busy devices are shown.

If a filter pattern looks like a number, append `0` so it is not treated as the refresh interval:

```bash
statblk nvme0 0    # match nvme0, single run (no watch)
```

## Platform notes

### Linux

Uses sysfs, `/proc/self/mountinfo`, `lsblk`, and optionally `smartctl`.

- **SMART** requires `smartctl` (smartmontools). Use `--sudo` if permission is denied.
- **READ / WRITE** throughput comes from `/sys/class/block/*/stat`.

### macOS

Uses `diskutil` and `mount`. Throughput columns are always zero (no per-device sysfs stats).

## Development

Run embedded doctests:

```bash
python -m doctest statblk.py -v
python statblk.py --doctest
```

## License

GPLv3+ — Yufei Pan ([pan@zopyr.us](mailto:pan@zopyr.us))

Project home: [github.com/yufei-pan/statblk](https://github.com/yufei-pan/statblk)
