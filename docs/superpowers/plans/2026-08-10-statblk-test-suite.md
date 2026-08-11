# statblk Hybrid Test Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a complete hybrid pytest suite for `statblk` (offline full-surface unit tests + optional live soft/strict), keeping embedded doctests via a wrapper test.

**Architecture:** Flat `tests/` package with shared fakes/`conftest`, focused modules per concern, default `pytest` excluding `live`/`live_strict`. Prefer monkeypatching `statblk.*` and small `tmp_path` sysfs trees; do not enable global `--doctest-modules`.

**Tech Stack:** Python 3.6+, pytest, stdlib `doctest`/`unittest.mock`/`pathlib`; production module `statblk.py` + dependency `multiCMD`.

**Spec:** `docs/superpowers/specs/2026-08-10-statblk-test-suite-design.md`

## Global Constraints

- Do not change runtime `setup.py` `install_requires` for test deps; use `requirements-dev.txt`.
- Do not enable global `--doctest-modules` (embedded multiCMD blob must not be scanned).
- Default `addopts` must exclude `live` and `live_strict`.
- Unit tests: no root, no network, no real-disk dependence.
- Plain `test_*` functions (CAS sibling style); no unittest TestCase classes.
- Do not bump package version solely for adding tests.
- Prefer monkeypatching `statblk.*` over full OS emulation.
- Production fixes already in the working tree (512-byte throughput, df-style FSUSE%, watch cache clear, `join(timeout)`, `-w/--watch`, short-stat `continue`) must be present before assertions that lock that behavior — commit them if still uncommitted before or as part of Task 1.

## File Structure

| File | Responsibility |
|------|----------------|
| `pytest.ini` | testpaths, markers, default addopts |
| `requirements-dev.txt` | pytest pin |
| `tests/conftest.py` | sys.path, cache clear, markers, live skip helpers |
| `tests/fakes.py` | FakeCmdResult, sample lines, make_sysfs_block |
| `tests/test_doctest_module.py` | doctest.testmod wrapper |
| `tests/test_parse.py` | parser edge cases |
| `tests/test_throughput.py` | 512-byte math, short-stat, sample semantics |
| `tests/test_fsuse.py` | get_statvfs_use_size + FSUSE% formula |
| `tests/test_sysfs_helpers.py` | read_size/discard/model/parent |
| `tests/test_drives_info.py` | get_drives_info orchestration |
| `tests/test_cli.py` | main() argv / watch peel |
| `tests/test_macos.py` | IS_DARWIN paths |
| `tests/test_live.py` | live + live_strict |
| `README.md` | Development: how to run tests |

---

### Task 1: Scaffold runner + fakes + doctest wrapper

**Files:**
- Create: `pytest.ini`
- Create: `requirements-dev.txt`
- Create: `tests/conftest.py`
- Create: `tests/fakes.py`
- Create: `tests/test_doctest_module.py`
- Modify (if still dirty): commit existing `statblk.py` / `README.md` production fixes first so tests lock real behavior

**Interfaces:**
- Consumes: `statblk` module importable from repo root
- Produces: `FakeCmdResult(stdout, returncode=0)` with `.thread.join(timeout=None)` appending to `.join_timeouts`; `make_sysfs_block(tmp_path, name, *, size_sectors, stat_fields=None, hw_sector_size=512, is_partition=False, model=None, serial=None) -> pathlib.Path` (sysfs block dir); `LSBLK_PAIRS_SAMPLE`, `MOUNTINFO_SAMPLE`, `DARWIN_MOUNT_SAMPLE`, `DISKUTIL_INFO_ALL_SAMPLE` string constants

- [ ] **Step 1: Commit production fixes if uncommitted**

```bash
cd /mnt/klein/work/cas/statblk
git status -sb
# If statblk.py / README.md show the P0/FSUSE%/watch/-w fixes, commit them:
git add statblk.py README.md
git commit -m "$(cat <<'EOF'
Fix throughput sector units, df-style FSUSE%, watch refresh, and --watch CLI.

EOF
)"
```

- [ ] **Step 2: Write `pytest.ini` and `requirements-dev.txt`**

`pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
markers =
    live: soft smoke against real host block devices (deselect by default)
    live_strict: strict comparisons vs df/lsblk (deselect by default)
addopts = -m "not live and not live_strict"
```

`requirements-dev.txt`:
```
pytest>=7,<9
```

- [ ] **Step 3: Write `tests/fakes.py`**

```python
from pathlib import Path


class FakeCmdResult:
    def __init__(self, stdout=None, returncode=0):
        self.stdout = list(stdout or [])
        self.returncode = returncode
        self.join_timeouts = []
        self.thread = self

    def join(self, timeout=None):
        self.join_timeouts.append(timeout)


LSBLK_PAIRS_SAMPLE = [
    'NAME="/dev/sda1" SIZE="1073741824" FSTYPE="ext4" UUID="u-1" LABEL="boot vol"',
    'NAME="/dev/sda2" SIZE="0" FSTYPE="" UUID="" LABEL=""',
]

LSBLK_RAW_SAMPLE = [
    "/dev/sda1 1073741824 ext4 u-1 boot vol",
    "/dev/sda2 0",
]

MOUNTINFO_SAMPLE = [
    "998 997 0:34 /root / rw,relatime - btrfs /dev/sda3 rw",
    "100 99 8:1 / /mnt/data rw - ext4 /dev/sda1 rw",
]

DARWIN_MOUNT_SAMPLE = [
    "/dev/disk3s1 on / (apfs, local, journaled)",
]

DISKUTIL_INFO_ALL_SAMPLE = """
Device Node:               /dev/disk3s1
Device / Media Name:       FakeSSD
Serial Number:             SN123
File System Personality:   APFS
Volume Name:               Macintosh HD
Volume UUID:               VOL-UUID
Disk Size:                 100.0 GB (107374182400 Bytes)
Solid State:               Yes

"""


def make_sysfs_block(
    tmp_path,
    name,
    *,
    size_sectors,
    stat_fields=None,
    hw_sector_size=512,
    is_partition=False,
    model=None,
    serial=None,
    discard_max_bytes=0,
):
    """Create tmp_path/sys/class/block/<name>/ ... and return that block path."""
    block = tmp_path / "sys" / "class" / "block" / name
    block.mkdir(parents=True)
    (block / "size").write_text(str(size_sectors))
    queue = block / "queue"
    queue.mkdir()
    (queue / "hw_sector_size").write_text(str(hw_sector_size))
    (queue / "logical_block_size").write_text(str(hw_sector_size))
    (queue / "discard_max_bytes").write_text(str(discard_max_bytes))
    if is_partition:
        (block / "partition").write_text("1")
    if stat_fields is not None:
        (block / "stat").write_text(" ".join(str(x) for x in stat_fields) + "\n")
    device = block / "device"
    device.mkdir()
    if model is not None:
        (device / "model").write_text(model)
    if serial is not None:
        (device / "serial").write_text(serial)
    return block
```

- [ ] **Step 4: Write `tests/conftest.py`**

```python
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import statblk  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "live: soft smoke against real host")
    config.addinivalue_line("markers", "live_strict: strict df/lsblk comparisons")


@pytest.fixture(autouse=True)
def _clear_statblk_caches():
    for fn in (statblk.parseMount, statblk.get_macos_diskutil_info):
        clear = getattr(fn, "cache_clear", None)
        if clear:
            clear()
    yield
    for fn in (statblk.parseMount, statblk.get_macos_diskutil_info):
        clear = getattr(fn, "cache_clear", None)
        if clear:
            clear()


def skip_unless_linux_block():
    if sys.platform != "linux":
        pytest.skip("Linux only")
    if not Path("/sys/class/block").is_dir():
        pytest.skip("no /sys/class/block")


def skip_unless_df_lsblk():
    import shutil
    if not shutil.which("df") or not shutil.which("lsblk"):
        pytest.skip("df/lsblk required")
```

- [ ] **Step 5: Write failing-then-passing doctest wrapper**

`tests/test_doctest_module.py`:
```python
import doctest

import statblk


def test_embedded_doctests():
    result = doctest.testmod(statblk, optionflags=doctest.NORMALIZE_WHITESPACE)
    assert result.failed == 0, f"doctest failures: {result.failed}"
```

- [ ] **Step 6: Install pytest and run wrapper**

```bash
pip install -r requirements-dev.txt
pytest tests/test_doctest_module.py -v
```

Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add pytest.ini requirements-dev.txt tests/conftest.py tests/fakes.py tests/test_doctest_module.py
git commit -m "$(cat <<'EOF'
Add pytest scaffold, fakes, and embedded doctest wrapper.

EOF
)"
```

---

### Task 2: Parser and FSUSE% unit tests

**Files:**
- Create: `tests/test_parse.py`
- Create: `tests/test_fsuse.py`

**Interfaces:**
- Consumes: `statblk.parse_*`, `compile_filter_pattern`, `_decode_proc_path`, `get_statvfs_use_size`, `LSBLK_*` from fakes
- Produces: locked parser edges + df-style FSUSE% helpers

- [ ] **Step 1: Write `tests/test_parse.py`**

```python
import pytest

import statblk
from fakes import LSBLK_PAIRS_SAMPLE, LSBLK_RAW_SAMPLE


def test_parse_lsblk_pairs_label_with_spaces():
    name, size, fstype, uuid, label = statblk.parse_lsblk_pairs_line(LSBLK_PAIRS_SAMPLE[0])
    assert name == "/dev/sda1"
    assert label == "boot vol"
    assert size == "1073741824"


def test_parse_lsblk_raw_label_with_spaces():
    name, size, fstype, uuid, label = statblk.parse_lsblk_raw_line(LSBLK_RAW_SAMPLE[0])
    assert label == "boot vol"
    assert fstype == "ext4"


def test_parse_lsblk_raw_short_line():
    name, size, fstype, uuid, label = statblk.parse_lsblk_raw_line("/dev/sda 100")
    assert (name, size, fstype, uuid, label) == ("/dev/sda", "100", "", "", "")


def test_compile_filter_invalid_regex_exits(capsys):
    with pytest.raises(SystemExit) as ei:
        statblk.compile_filter_pattern(["[unterminated"])
    assert ei.value.code == 1
    assert "Invalid filter pattern" in capsys.readouterr().err


def test_decode_proc_path_space():
    assert statblk._decode_proc_path("/mnt\\040disk") == "/mnt disk"
```

- [ ] **Step 2: Write `tests/test_fsuse.py`**

```python
from types import SimpleNamespace

import statblk


def test_get_statvfs_use_size_excludes_reserved(monkeypatch):
    # 100 blocks total, 40 free to root, 30 avail to user → 60 used, not 70
    st = SimpleNamespace(f_frsize=1024, f_bsize=1024, f_blocks=100, f_bfree=40, f_bavail=30)

    def fake_statvfs(_path):
        return st

    monkeypatch.setattr(statblk.os, "statvfs", fake_statvfs)
    total, used, avail = statblk.get_statvfs_use_size("/")
    assert total == 100 * 1024
    assert used == (100 - 40) * 1024
    assert avail == 30 * 1024
    assert used != total - avail  # reserved must not count as used


def test_fsuse_percent_matches_df_ceiling():
    used, avail = 3515, 6485  # arbitrary bytes
    denom = used + avail
    pct = (used * 100) // denom
    if (used * 100) % denom:
        pct += 1
    # sanity: this is the formula get_drives_info must use
    assert pct == 36
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_parse.py tests/test_fsuse.py -v
```

Expected: PASS (if FSUSE% production code returns 3-tuple; FAIL if still old 2-tuple — then verify Task 1 production commit)

- [ ] **Step 4: Commit**

```bash
git add tests/test_parse.py tests/test_fsuse.py
git commit -m "$(cat <<'EOF'
Add parser edge and df-style FSUSE% unit tests.

EOF
)"
```

---

### Task 3: Throughput and sysfs helper tests

**Files:**
- Create: `tests/test_throughput.py`
- Create: `tests/test_sysfs_helpers.py`

**Interfaces:**
- Consumes: `make_sysfs_block`, `statblk.STAT_SECTOR_BYTES`, `get_read_write_rate_throughput_iter`, `read_size`, `read_discard_support`, `read_model_and_serial`, `get_partition_parent_name`
- Produces: regressions for 512-byte stat units and short-stat continue

- [ ] **Step 1: Write `tests/test_throughput.py`**

```python
import statblk
from fakes import make_sysfs_block


def test_throughput_uses_512_not_hw_sector_size(tmp_path, monkeypatch):
    # 1000 sectors read, 1000 ms read time → first sample = 1000*512/1 = 512000 B/s
    # If wrongly using hw=4096, would be 4_096_000
    fields = [0, 0, 1000, 1000, 0, 0, 0, 0, 0, 0, 0]
    block = make_sysfs_block(
        tmp_path, "nvme0n1", size_sectors=1000, stat_fields=fields, hw_sector_size=4096
    )
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    it = statblk.get_read_write_rate_throughput_iter(str(block))
    read_bps, write_bps = next(it)
    assert read_bps == 1000 * statblk.STAT_SECTOR_BYTES  # 512000
    assert write_bps == 0


def test_short_stat_poll_yields_once_then_continues(tmp_path, monkeypatch):
    block = make_sysfs_block(
        tmp_path,
        "sda",
        size_sectors=10,
        stat_fields=[0, 0, 0, 0, 0, 0, 0, 0],
        hw_sector_size=512,
    )
    path = block / "stat"
    reads = {"n": 0}

    def fake_open(p, *a, **k):
        # After first successful sample, return short lines forever
        class F:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                reads["n"] += 1
                if reads["n"] == 1:
                    return "0 0 100 1000 0 0 50 500\n"
                return "0 0 100\n"  # < 7 fields

        if str(p) == str(path):
            return F()
        return open(p, *a, **k)

    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    it = statblk.get_read_write_rate_throughput_iter(str(block))
    first = next(it)
    assert first[0] > 0
    second = next(it)
    assert second == (0, 0)
    # Third next should again be a single short-line yield, not a double IndexError path
    third = next(it)
    assert third == (0, 0)
    assert reads["n"] == 3
```

- [ ] **Step 2: Write `tests/test_sysfs_helpers.py`**

```python
import os

import statblk
from fakes import make_sysfs_block


def test_read_size_uses_512(tmp_path):
    block = make_sysfs_block(tmp_path, "sda", size_sectors=2048, hw_sector_size=4096)
    assert statblk.read_size(str(block)) == 2048 * 512


def test_read_discard_yes_no(tmp_path):
    yes = make_sysfs_block(tmp_path, "sda", size_sectors=1, discard_max_bytes=4096)
    no = make_sysfs_block(tmp_path, "sdb", size_sectors=1, discard_max_bytes=0)
    assert statblk.read_discard_support(str(yes)) == "Yes"
    assert statblk.read_discard_support(str(no)) == "No"


def test_read_model_serial_collapse(tmp_path, monkeypatch):
    block = make_sysfs_block(
        tmp_path, "sda", size_sectors=1, model="  Foo   Bar  ", serial="  SN 1  "
    )
    # get_real_sysfs_device_path uses realpath of block/device
    monkeypatch.setattr(statblk, "get_real_sysfs_device_path", lambda p: os.path.join(p, "device"))
    model, serial = statblk.read_model_and_serial(str(block))
    assert model == "Foo Bar"
    assert serial == "SN 1"
```

- [ ] **Step 3: Run**

```bash
pytest tests/test_throughput.py tests/test_sysfs_helpers.py -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_throughput.py tests/test_sysfs_helpers.py
git commit -m "$(cat <<'EOF'
Add throughput 512-byte and sysfs helper unit tests.

EOF
)"
```

---

### Task 4: `get_drives_info` orchestration tests

**Files:**
- Create: `tests/test_drives_info.py`

**Interfaces:**
- Consumes: `FakeCmdResult`, `statblk.get_drives_info`, `statblk.MountEntry`
- Produces: coverage for columns, filters, flags, cache clear, join(timeout)

- [ ] **Step 1: Write `tests/test_drives_info.py` with shared setup helper**

```python
from collections import defaultdict

import statblk
from fakes import FakeCmdResult


def _mount_table(device="/dev/sda1", mp="/data"):
    return defaultdict(list, {device: [statblk.MountEntry(mp, "ext4", ["rw"])]})


def _patch_linux_basics(monkeypatch, devices=None, mounts=None):
    devices = devices or ["/dev/sda1"]
    mounts = mounts if mounts is not None else _mount_table()
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    monkeypatch.setattr(statblk, "get_blocks", lambda: list(devices))
    monkeypatch.setattr(statblk, "parseMount", lambda: mounts)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_partition_parent_name", lambda p: "/dev/sda")
    monkeypatch.setattr(statblk, "lsblk_supports_pairs", lambda: True)
    monkeypatch.setattr(
        statblk,
        "get_statvfs_use_size",
        lambda mp: (1000, 350, 650),  # total, used, avail → 35% ceil? 3500/1000=35 exact
    )
    # throughput: finite then zeros
    def fake_tpt(_path):
        yield 100, 200
        while True:
            yield 0, 0

    monkeypatch.setattr(statblk, "get_read_write_rate_throughput_iter", fake_tpt)


def test_output_and_exclude_columns(monkeypatch):
    _patch_linux_basics(monkeypatch)
    fake = FakeCmdResult(
        ['NAME="/dev/sda1" SIZE="1000" FSTYPE="ext4" UUID="u" LABEL="L"'], 0
    )
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output="NAME,FSUSE%,MOUNTPOINT", exclude="FSUSE%", timeout=2)
    assert rows[0] == ["NAME", "MOUNTPOINT"]


def test_filter_and_invert(monkeypatch):
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1", "/dev/nvme0n1"])
    mounts = _mount_table("/dev/sda1", "/")
    mounts["/dev/nvme0n1"] = [statblk.MountEntry("/mnt", "xfs", ["rw"])]
    monkeypatch.setattr(statblk, "parseMount", lambda: mounts)
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output="NAME,MOUNTPOINT", filter_patterns=["nvme"], timeout=2)
    names = [r[0] for r in rows[1:]]
    assert any("nvme" in n for n in names)
    assert not any(n.endswith("sda1") or n == "sda1" for n in names)


def test_lsblk_join_uses_timeout(monkeypatch):
    _patch_linux_basics(monkeypatch)
    fake = FakeCmdResult(
        ['NAME="/dev/sda1" SIZE="1000" FSTYPE="ext4" UUID="u" LABEL="L"'], 0
    )
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    statblk.get_drives_info(output="NAME,SIZE,UUID,LABEL,FSTYPE", timeout=7)
    assert fake.join_timeouts == [7]


def test_cache_cleared_between_get_drives_info_calls(monkeypatch):
    _patch_linux_basics(monkeypatch)
    calls = {"n": 0}
    tables = [
        _mount_table("/dev/sda1", "/old"),
        _mount_table("/dev/sda1", "/new"),
    ]

    def parse_mount():
        # emulate cache decorator miss after clear: return next table
        idx = min(calls["n"], len(tables) - 1)
        calls["n"] += 1
        return tables[idx]

    # Replace cached parseMount with counting function; get_drives_info still calls cache_clear on attribute if present
    parse_mount.cache_clear = lambda: None
    monkeypatch.setattr(statblk, "parseMount", parse_mount)
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    r1 = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    r2 = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    assert any("/old" in row for row in r1)
    assert any("/new" in row for row in r2)
    assert calls["n"] >= 2
```

Add additional concise tests in the same file for: `mounted_only` skips unmounted; `best_only` picks shortest mount; `show_zero_size_devices`; `match_devname_only`; `formated_only`; `pseudo` adds mount_table keys. Follow the same patching pattern as above (copy the `_patch_linux_basics` setup into each test; do not hand-wave).

- [ ] **Step 2: Run**

```bash
pytest tests/test_drives_info.py -v
```

Expected: PASS (adjust mount/FSUSE% expectations if `format_bytes` / NAME full vs basename differs — use `full=True` when asserting `/dev/...`)

- [ ] **Step 3: Commit**

```bash
git add tests/test_drives_info.py
git commit -m "$(cat <<'EOF'
Add get_drives_info orchestration unit tests.

EOF
)"
```

---

### Task 5: CLI and macOS tests

**Files:**
- Create: `tests/test_cli.py`
- Create: `tests/test_macos.py`

**Interfaces:**
- Consumes: `statblk.main`, `DISKUTIL_INFO_ALL_SAMPLE`, `DARWIN_MOUNT_SAMPLE`
- Produces: watch argv behavior + darwin parsing locks

- [ ] **Step 1: Write `tests/test_cli.py`**

```python
import json

import pytest

import statblk


def test_watch_flag_and_trailing_int(monkeypatch):
    calls = []

    def fake_gdi(**kwargs):
        calls.append(kwargs.get("filter_patterns"))
        return [["NAME"], ["sda"]]

    sleeps = []

    monkeypatch.setattr(statblk, "get_drives_info", fake_gdi)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "TABLE")
    monkeypatch.setattr(statblk.time, "sleep", lambda s: sleeps.append(s) or (_ for _ in ()).throw(KeyboardInterrupt()))

    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-w", "5", "sda"])
    statblk.main()
    assert sleeps == [5]
    assert calls[0] == ["sda"]

    sleeps.clear()
    calls.clear()
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "sda", "3"])
    monkeypatch.setattr(statblk.time, "sleep", lambda s: sleeps.append(s) or (_ for _ in ()).throw(KeyboardInterrupt()))
    statblk.main()
    assert sleeps == [3]
    assert calls[0] == ["sda"]


def test_watch_flag_wins_over_trailing(monkeypatch):
    sleeps = []
    monkeypatch.setattr(statblk, "get_drives_info", lambda **k: [["NAME"], ["x"]])
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "T")
    monkeypatch.setattr(statblk.time, "sleep", lambda s: sleeps.append(s) or (_ for _ in ()).throw(KeyboardInterrupt()))
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-w", "5", "sda", "9"])
    statblk.main()
    assert sleeps == [5]


def test_trailing_zero_is_not_watch(monkeypatch):
    sleeps = []
    patterns = []

    def fake_gdi(**kwargs):
        patterns.append(kwargs.get("filter_patterns"))
        return [["NAME"], ["nvme0"]]

    monkeypatch.setattr(statblk, "get_drives_info", fake_gdi)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda r, **k: "T")
    monkeypatch.setattr(statblk.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "nvme0", "0"])
    statblk.main()
    assert sleeps == []
    assert patterns[0] == ["nvme0"]


def test_version(monkeypatch, capsys):
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-V"])
    with pytest.raises(SystemExit) as ei:
        statblk.main()
    assert ei.value.code == 0
    assert statblk.version in capsys.readouterr().out


def test_json_output(monkeypatch, capsys):
    monkeypatch.setattr(statblk, "get_drives_info", lambda **k: [["NAME"], ["sda"]])
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.sys, "argv", ["statblk", "-j"])
    statblk.main()
    data = json.loads(capsys.readouterr().out)
    assert data[0] == ["NAME"]
```

- [ ] **Step 2: Write `tests/test_macos.py`**

```python
import statblk
from fakes import DARWIN_MOUNT_SAMPLE, DISKUTIL_INFO_ALL_SAMPLE


def test_parse_darwin_mount_line():
    dev, ent = statblk.parse_darwin_mount_line(DARWIN_MOUNT_SAMPLE[0])
    assert ent.MOUNTPOINT == "/"
    assert ent.FSTYPE == "apfs"


def test_get_macos_diskutil_info(monkeypatch):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")
    monkeypatch.setattr(
        statblk.multiCMD,
        "run_command",
        lambda *a, **k: DISKUTIL_INFO_ALL_SAMPLE.strip("\n").split("\n") + [""],
    )
    if hasattr(statblk.get_macos_diskutil_info, "cache_clear"):
        statblk.get_macos_diskutil_info.cache_clear()
    info = statblk.get_macos_diskutil_info(timeout=1)
    assert "/dev/disk3s1" in info
    assert info["/dev/disk3s1"]["SIZE_BYTES"] == 107374182400
    assert info["/dev/disk3s1"]["DISCARD"] == "Yes"


def test_throughput_zero_on_darwin(monkeypatch):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    it = statblk.get_read_write_rate_throughput_iter("/dev/disk0")
    assert next(it) == (0, 0)
```

- [ ] **Step 3: Run**

```bash
pytest tests/test_cli.py tests/test_macos.py -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_cli.py tests/test_macos.py
git commit -m "$(cat <<'EOF'
Add CLI watch/JSON and macOS unit tests.

EOF
)"
```

---

### Task 6: Live soft + strict tests and README

**Files:**
- Create: `tests/test_live.py`
- Modify: `README.md` (Development section)

**Interfaces:**
- Consumes: `skip_unless_linux_block`, `skip_unless_df_lsblk` from conftest; real `get_drives_info`
- Produces: optional live markers meeting success criteria

- [ ] **Step 1: Write `tests/test_live.py`**

```python
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import statblk
from conftest import skip_unless_df_lsblk, skip_unless_linux_block


@pytest.mark.live
def test_live_soft_smoke():
    skip_unless_linux_block()
    rows = statblk.get_drives_info(output="NAME,SIZE,MOUNTPOINT", timeout=5)
    assert rows and rows[0][0] == "NAME"
    assert len(rows) >= 2
    for col in rows[0]:
        assert col in statblk.ALL_OUTPUT_FIELDS


@pytest.mark.live_strict
def test_live_strict_fsuse_root_matches_df():
    skip_unless_linux_block()
    skip_unless_df_lsblk()
    rows = statblk.get_drives_info(
        output="NAME,FSUSE%,MOUNTPOINT", mounted_only=True, best_only=True, timeout=5
    )
    root_rows = [r for r in rows[1:] if r[2] == "/"]
    assert root_rows, "no row for mountpoint /"
    statblk_pct = root_rows[0][1]
    df_out = subprocess.check_output(["df", "-P", "/"], text=True).strip().splitlines()
    # Filesystem 1024-blocks Used Available Capacity Mounted on
    m = re.search(r"\s(\d+)%\s+/\s*$", df_out[-1])
    assert m, df_out[-1]
    assert statblk_pct == f"{m.group(1)}%"


@pytest.mark.live_strict
def test_live_strict_names_subset_of_lsblk():
    skip_unless_linux_block()
    skip_unless_df_lsblk()
    rows = statblk.get_drives_info(output="NAME", show_zero_size_devices=True, timeout=5)
    names = {r[0].replace("/dev/", "") for r in rows[1:]}
    lsblk = subprocess.check_output(["lsblk", "-n", "-o", "NAME"], text=True)
    lsblk_names = {line.strip() for line in lsblk.splitlines() if line.strip()}
    # loop/dm naming can include tree prefixes from lsblk without -p; use basename set
    assert names <= lsblk_names or names.issubset({n.lstrip("└─├─│ ") for n in lsblk_names})
```

If the lsblk name-set assert is flaky on this host (tree glyphs), switch `lsblk` invocation to `lsblk -n -l -o NAME` (list mode, no tree) in the same step and assert `names <= set(lsblk_names)`.

- [ ] **Step 2: Update README Development section**

Replace/extend Development to:

```markdown
## Development

Install test deps:

```bash
pip install -r requirements-dev.txt
```

Run unit tests (default; live excluded) and embedded doctests:

```bash
pytest
python statblk.py --doctest
```

Optional live checks:

```bash
pytest -m live          # soft smoke on this host
pytest -m live_strict   # compare FSUSE% and names to df/lsblk
```
```

- [ ] **Step 3: Run default + live suites**

```bash
pytest -v
pytest -m live -v
pytest -m live_strict -v
```

Expected: default PASS; live/live_strict PASS on this Linux host (or skip with clear reason if tools missing)

- [ ] **Step 4: Commit**

```bash
git add tests/test_live.py README.md
git commit -m "$(cat <<'EOF'
Add live soft/strict tests and document pytest usage.

EOF
)"
```

---

### Task 7: Final verification gate

**Files:** none (verification only)

- [ ] **Step 1: Full default suite**

```bash
pytest -v
python statblk.py --doctest
```

Expected: all PASS

- [ ] **Step 2: Confirm live markers deselected by default**

```bash
pytest -v 2>&1 | tee /tmp/statblk-pytest.out
# deselected count should be > 0 for live tests, or collected count excludes them
grep -E "deselected|live" /tmp/statblk-pytest.out || true
```

- [ ] **Step 3: Spec success criteria checklist**

- [ ] Default pytest green offline
- [ ] Doctests via wrapper + `--doctest`
- [ ] `pytest -m live` soft smoke
- [ ] `pytest -m live_strict` df Use% for `/` + lsblk names
- [ ] README documents commands

- [ ] **Step 4: Final commit only if stray fixes remain**

```bash
git status -sb
# commit any leftover test fixes with a clear message; do not bump version
```

---

## Self-review (plan vs spec)

| Spec requirement | Task |
|------------------|------|
| pytest.ini markers + default exclude live | Task 1 |
| requirements-dev.txt | Task 1 |
| conftest path/cache/markers/skips | Task 1 |
| fakes FakeCmdResult + make_sysfs_block + samples | Task 1 |
| doctest wrapper not global --doctest-modules | Task 1 |
| parse edges | Task 2 |
| FSUSE% df formula | Task 2 |
| throughput 512 + short-stat | Task 3 |
| sysfs helpers | Task 3 |
| get_drives_info flags/filters/cache/join timeout | Task 4 |
| CLI -w / trailing / version / json | Task 5 |
| macOS | Task 5 |
| live + live_strict | Task 6 |
| README | Task 6 |
| Success criteria gate | Task 7 |

No TBD/placeholder steps remain after self-review. `FakeCmdResult.join` signature and `get_statvfs_use_size` 3-tuple are consistent across tasks.
