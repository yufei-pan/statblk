# statblk test suite design

Date: 2026-08-10  
Status: approved for spec review (pending user sign-off of this document)

## Goal

Build a complete hybrid test suite for `statblk`: offline unit/regression coverage of the full public surface, plus optional live soft smoke and opt-in strict comparisons against `df`/`lsblk`. Keep embedded doctests; collect them via pytest.

## Decisions (from brainstorming)

| Topic | Choice |
|-------|--------|
| Strategy | Hybrid: mocked unit core + optional live |
| Doctests | Keep in `statblk.py`; pytest runs them via `test_embedded_doctests` wrapper (not global `--doctest-modules`) |
| Depth | Full surface (helpers + flags + orchestration) + richer live |
| Live strictness | Soft smoke by default; strict opt-in (`live_strict`) |
| Layout | Flat `tests/` package with focused modules (approach 1) |

## Layout

```
statblk/
  statblk.py
  pytest.ini
  requirements-dev.txt          # pytest (and pins if needed)
  tests/
    conftest.py
    fakes.py
    test_doctest_module.py      # wrapper around doctest.testmod(statblk)
    test_parse.py
    test_throughput.py
    test_fsuse.py
    test_sysfs_helpers.py
    test_drives_info.py
    test_cli.py
    test_macos.py
    test_live.py
  docs/superpowers/specs/
    2026-08-10-statblk-test-suite-design.md
```

Runtime `setup.py` `install_requires` stays unchanged. Document `pip install -r requirements-dev.txt` (or `pip install pytest`) in README under Development.

## Runner configuration (`pytest.ini`)

- `testpaths = tests`
- `python_files = test_*.py`
- Markers: `live`, `live_strict`
- Default `addopts = -m "not live and not live_strict"` so offline CI/dev is unit-only
- Do **not** enable global `--doctest-modules` (the embedded multiCMD base85/lzma blob in `statblk.py` must not be scanned as doctest text)
- Instead: `tests/test_doctest_module.py` with `test_embedded_doctests` calling `doctest.testmod(statblk, optionflags=doctest.NORMALIZE_WHITESPACE)` and asserting `failed == 0` (same flags as `statblk.py --doctest`)
- Optional: if `STATBLK_LIVE_STRICT=1` is set, `conftest.py` can auto-enable `live_strict` collection; primary interface remains `pytest -m live_strict`

### How to run

```bash
pytest                          # unit + embedded doctests wrapper
python statblk.py --doctest     # existing entry (still supported)
pytest -m live                  # soft smoke on real host
pytest -m live_strict           # strict df/lsblk agreement
```

## Shared fakes (`tests/fakes.py`)

- Sample fixtures: `lsblk -P` lines, raw lsblk lines, `/proc/self/mountinfo` lines, darwin `mount` lines, `diskutil info -all` blob
- `FakeCmdResult(stdout, returncode=0)` with `thread.join(timeout=None)` that records the wait argument into a list for assertions
- `make_sysfs_block(tmp_path, name, *, size_sectors, stat_fields=None, hw_sector_size=512, is_partition=False, model=None, serial=None)` → path usable by `read_*` / throughput helpers

## `conftest.py`

- Put repo root on `sys.path` so `import statblk` works without install
- Autouse fixture for non-live tests: clear `parseMount` / `get_macos_diskutil_info` caches when `cache_clear` exists
- Helpers to skip live tests when not Linux or `/sys/class/block` missing; skip live_strict when `df`/`lsblk` missing
- Register `live` and `live_strict` markers

## Coverage matrix

### Parsers (`test_parse.py` + embedded doctests)

- Doctests remain source of truth for happy-path parse helpers already documented
- Pytest adds edges: LABEL with spaces (pairs + raw), empty/short lines, `compile_filter_pattern` invalid regex → `SystemExit`, `_decode_proc_path` escapes

### Throughput (`test_throughput.py`)

- Fake `stat` under tmp sysfs with `hw_sector_size=4096` but assert byte math uses **512** (`STAT_SECTOR_BYTES`)
- Short `stat` line (`len(fields) < 7`): one `(0, 0)` yield and no double-advance on a single `next()` after a good sample setup — assert poll path uses `continue`
- Document/assert intentional first sample (busy-time average) vs later interval sample (Δbytes / wall clock); use controlled fake reads + time monkeypatch if needed

### FSUSE% (`test_fsuse.py`)

- Fake `os.statvfs` namespace: `used = (f_blocks - f_bfree) * frsize`, `avail = f_bavail * frsize`
- Percent matches GNU df ceiling style: `pct = (used*100)//denom; +1 if remainder`
- Reserved-space case: `f_bfree > f_bavail` must not inflate used

### Sysfs helpers (`test_sysfs_helpers.py`)

- `read_size` = sectors × 512
- `read_discard_support` Yes/No/N/A
- `read_model_and_serial` whitespace collapse
- `get_partition_parent_name` for disk vs partition (Linux paths; darwin via patch)

### Orchestration (`test_drives_info.py`)

Monkeypatch `get_blocks`, `parseMount`, `is_block_device`, lsblk/smartctl `FakeCmdResult`, `get_statvfs_use_size` / mounts as needed.

Must cover:

- `-o` / exclude column filtering; invalid field ignored
- Filters: normal, `-v` invert, `-D` match_devname_only
- `mounted_only`, `best_only`, `formated_only`, `pseudo`, `active_only`, `show_zero_size_devices`
- Watch-related: two successive `get_drives_info` calls see refreshed mount table (cache cleared at start of each call); throughput `tptDict` iterators remain live across calls
- `lsblk` / `smartctl` `thread.join` receives `timeout` (not hard-coded `1`)

### CLI (`test_cli.py`)

Drive `main()` via `sys.argv` monkeypatch; stub `get_drives_info` and `time.sleep` to avoid real I/O / hangs.

- `-w` / `--watch SECONDS` sets period
- Trailing integer peel: `statblk 5`, `statblk sda 3`, `statblk nvme0 0`
- Explicit `-w` wins when both `-w` and trailing int present
- `-V` / `--version` exits 0 and prints version
- `-j` JSON path (optional thin assert)

### macOS (`test_macos.py`)

- Patch `IS_DARWIN=True`
- `parse_darwin_mount_line` / `get_macos_diskutil_info` with fixture text
- Throughput iterator yields zeros on darwin

### Live (`test_live.py`)

**Soft (`@pytest.mark.live`)**

- Skip if not Linux or no `/sys/class/block`
- Run `get_drives_info` (or CLI once) with a small column set
- Assert: header row present; ≥1 data row; every column name ∈ `ALL_OUTPUT_FIELDS`

**Strict (`@pytest.mark.live_strict`)**

- Skip if `df` or `lsblk` missing
- For mount `/`: `FSUSE%` from `get_drives_info` matches `df` Use% for `/` exactly (same formula)
- Device basenames from `statblk` ⊆ names from `lsblk -n -o NAME` (allow `/dev/` prefix normalization)
- Do not require SMART agreement (permissions vary)

## Error / skip policy

- Unit tests: no root, no network, no dependence on real disks
- Live soft: skip when environment lacks block sysfs
- Live strict: skip when tools missing; fail only on clear field mismatches defined above
- Invalid filter pattern: expect controlled exit, not traceback sprawl

## Out of scope

- Fuzzing or validating the embedded multiCMD blob contents
- Real SMART hardware pass/fail semantics beyond parsing stdout fixtures
- Performance benchmarks
- Changing production packaging beyond documenting test deps

## Success criteria

1. `pytest` (default markers) passes with no live host requirements
2. Embedded doctests still pass (`statblk.py --doctest` and the pytest wrapper)
3. `pytest -m live` soft smoke passes on a normal Linux block host
4. `pytest -m live_strict` matches `df` Use% for `/` and lsblk name set containment
5. README Development section documents unit / live / live_strict commands

## Implementation notes (non-goals for this spec’s approval)

- Prefer monkeypatching `statblk.*` callables over full OS emulation
- Prefer `tmp_path` sysfs trees only for helpers that read paths directly
- Mirror sibling CAS style: plain `test_*` functions, pytest, no unittest classes
- Do not bump package version solely for adding tests unless releasing
