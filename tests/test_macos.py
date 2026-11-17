import os
import time
from collections import defaultdict

import pytest

import statblk
from fakes import DARWIN_MOUNT_SAMPLE, MACOS26_DEV, MACOS26_DISKUTIL, MACOS26_MOUNT, FakeCmdResult


def test_parse_darwin_mount_line():
    dev, ent = statblk.parse_darwin_mount_line(DARWIN_MOUNT_SAMPLE[0])
    assert ent.MOUNTPOINT == "/"
    assert ent.FSTYPE == "apfs"


def _diskutil_info(monkeypatch, lines, returncode=0):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: FakeCmdResult(lines, returncode))
    return statblk.get_macos_diskutil_info(timeout=1)


def test_get_macos_diskutil_info_reads_every_section(monkeypatch):
    # macOS 26 splits each device into sections with blank lines; 1.62 read only the first (no size, type or UUID).
    info = _diskutil_info(monkeypatch, MACOS26_DISKUTIL)
    assert sorted(info) == sorted(MACOS26_DEV)
    assert all(d["SIZE_BYTES"] for d in info.values())
    assert sum(d["FSTYPE"] == "APFS" for d in info.values()) == 13
    assert info["/dev/disk0"] == {"SIZE_BYTES": 500277792768, "FSTYPE": "", "UUID": "", "LABEL": "",
                                  "MODEL": "APPLE SSD AP0512Z", "SERIAL": "", "DISCARD": "Yes"}
    assert info["/dev/disk3s5"]["LABEL"] == "Volume 8"
    assert info["/dev/disk3s5"]["UUID"] == "00000000-0000-4000-8000-000000000014"


@pytest.mark.parametrize("size_line, expected", [
    ("   Disk Size:                 0 B (0 Bytes) (exactly 0 512-Byte-Units)", 0),
    ("   Disk Size:                 Not applicable (no media)", None),
    (None, None),  # diskutil was stopped before the line, or never prints it
])
def test_diskutil_size_none_when_it_gave_none(monkeypatch, size_line, expected):
    lines = ["   Device Identifier:         disk5", "   Device Node:               /dev/disk5", "",
             "   Solid State:               No"] + ([size_line] if size_line else [])
    assert _diskutil_info(monkeypatch, lines)["/dev/disk5"]["SIZE_BYTES"] == expected


def test_diskutil_stopped_mid_device_keeps_what_it_read(monkeypatch):
    lines = MACOS26_DISKUTIL[:MACOS26_DISKUTIL.index("   Device Node:               /dev/disk0s1") + 3]
    info = _diskutil_info(monkeypatch, lines, returncode=124)
    assert sorted(info) == ["/dev/disk0", "/dev/disk0s1"]
    assert info["/dev/disk0"]["SIZE_BYTES"] == 500277792768 and info["/dev/disk0s1"]["SIZE_BYTES"] is None


def _darwin_machine(monkeypatch, dev=MACOS26_DEV, mount=(MACOS26_MOUNT, 0), diskutil=(MACOS26_DISKUTIL, 0)):
    """get_drives_info on the test Mac's own output: its /dev nodes, and mount and diskutil as (lines, return code);
    statvfs and smartctl faked."""
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", None)
    _fake_dev_listing(monkeypatch, [d[len("/dev/"):] for d in dev])
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p in dev)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    monkeypatch.setattr(statblk.multiCMD, "run_command",
                        lambda command, **k: FakeCmdResult(*(mount if command == "mount" else diskutil)))


def _names(rows):
    return [r[0] for r in rows[1:]]


ALL_NAMES = [d[len("/dev/"):] for d in MACOS26_DEV]
UNMOUNTED = ["disk0", "disk0s1", "disk0s2", "disk0s3", "disk1", "disk1s4", "disk2", "disk2s1", "disk2s2", "disk3",
             "disk3s1", "disk3s3"]
# diskutil's lines up to disk1's Device Node: disk0 and its partitions only
BEFORE_DISK1 = MACOS26_DISKUTIL[:MACOS26_DISKUTIL.index("   Device Node:               /dev/disk1")]


def test_unmounted_whole_disk_gets_its_size(monkeypatch):
    _darwin_machine(monkeypatch)
    rows = statblk.get_drives_info(output="NAME,SIZE,MOUNTPOINT", timeout=2)
    assert [r[0] for r in rows[1:]] == [d[len("/dev/"):] for d in MACOS26_DEV]  # every device is listed
    assert ["disk0", "500277792768B", ""] in rows
    assert ["disk3s1s1", "1000B", "/"] in rows


def test_throughput_zero_on_darwin(monkeypatch):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    it = statblk.get_read_write_rate_throughput_iter("/dev/disk0")
    assert next(it) == (0, 0)


def _fake_dev_listing(monkeypatch, entries):
    real_listdir = os.listdir
    monkeypatch.setattr(
        statblk.os, "listdir", lambda p: list(entries) if p == "/dev" else real_listdir(p)
    )


def test_get_blocks_includes_apfs_snapshot_nodes(monkeypatch):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    _fake_dev_listing(monkeypatch, ["disk0", "disk0s1", "disk3s1s1", "disk3s1", "diskX", "null"])
    assert statblk.get_blocks() == ["/dev/disk0", "/dev/disk0s1", "/dev/disk3s1", "/dev/disk3s1s1"]


def test_partition_parent_of_apfs_snapshot(monkeypatch):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p == "/dev/disk3")
    assert statblk.get_partition_parent_name("disk3s1s1") == "/dev/disk3"


def test_darwin_sealed_root_listed_without_pseudo(monkeypatch):
    # macOS 11+: `/dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled)`
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    _fake_dev_listing(monkeypatch, ["disk3", "disk3s1", "disk3s1s1"])
    mounts = defaultdict(list, {"/dev/disk3s1s1": [statblk.MountEntry("/", "apfs", ["apfs", "sealed"])]})
    monkeypatch.setattr(statblk, "parseMount", lambda timeout=0, cut=None: mounts)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    # No diskutil column, so no size was read for the unmounted disk3 and disk3s1: they stay, as rows with no SIZE.
    assert rows[1:] == [["disk3", ""], ["disk3s1", ""], ["disk3s1s1", "/"]]


@pytest.mark.parametrize("output", ["NAME,SIZE", "NAME,MOUNTPOINT"])
def test_darwin_formated_only_without_fstype_column(monkeypatch, output):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    _fake_dev_listing(monkeypatch, ["disk4s1", "disk4s2"])
    monkeypatch.setattr(statblk, "parseMount", lambda timeout=0, cut=None: defaultdict(list))
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    info = {
        "/dev/disk4s1": {"SIZE_BYTES": 1000, "FSTYPE": "ExFAT"},
        "/dev/disk4s2": {"SIZE_BYTES": 2000, "FSTYPE": ""},
    }
    monkeypatch.setattr(statblk, "get_macos_diskutil_info", lambda timeout=0, cut=None: info)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output=output, formated_only=True, timeout=2)
    assert [r[0] for r in rows[1:]] == ["disk4s1"]


@pytest.mark.parametrize("timeout, expected", [
    (0, 0),      # -t 0: no limit, as for lsblk, smartctl and statvfs
    (None, 0),   # the library default means no limit too
    (3, 3),      # a non-zero -t bounds diskutil and mount as it bounds the rest
    (0.5, 0.5),
])
def test_darwin_diskutil_and_mount_get_the_timeout(monkeypatch, timeout, expected):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")
    _fake_dev_listing(monkeypatch, ["disk3", "disk3s1"])
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    calls = {}

    def fake_run_command(command, timeout=0, **kwargs):
        calls[command.split()[0].rsplit("/", 1)[-1]] = timeout
        if command == "mount":
            return FakeCmdResult(DARWIN_MOUNT_SAMPLE)
        return FakeCmdResult(MACOS26_DISKUTIL)

    monkeypatch.setattr(statblk.multiCMD, "run_command", fake_run_command)
    statblk.get_drives_info(output="NAME,SIZE,MOUNTPOINT", timeout=timeout)
    assert calls == {"diskutil": expected, "mount": expected}


@pytest.mark.parametrize("returncode, expected", [(124, ["diskutil", "mount"]), (0, []), (1, [])])
def test_diskutil_and_mount_stopped_by_the_timeout_are_recorded(monkeypatch, returncode, expected):
    # 124 is multiCMD's return code for a command it stopped at the timeout; what it printed before is still read.
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")

    def fake_run_command(command, timeout=0, **kwargs):
        if command == "mount":
            return FakeCmdResult(DARWIN_MOUNT_SAMPLE, returncode)
        return FakeCmdResult(MACOS26_DISKUTIL, returncode)

    monkeypatch.setattr(statblk.multiCMD, "run_command", fake_run_command)
    cut = []
    assert "/dev/disk3s1" in statblk.get_macos_diskutil_info(timeout=1, cut=cut)
    assert list(statblk.parseMount(1, cut=cut)) == ["/dev/disk3s1"]
    assert cut == expected


@pytest.mark.parametrize("returncode, expected", [(124, ["diskutil", "mount"]), (0, [])])
def test_get_drives_info_passes_cut_to_diskutil_and_mount(monkeypatch, returncode, expected):
    # The whole path: what main() prints and decides from comes through get_drives_info's own `cut`.
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")
    _fake_dev_listing(monkeypatch, ["disk3", "disk3s1"])
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))

    def fake_run_command(command, timeout=0, **kwargs):
        if command == "mount":
            return FakeCmdResult(DARWIN_MOUNT_SAMPLE, returncode)
        return FakeCmdResult(MACOS26_DISKUTIL, returncode)

    monkeypatch.setattr(statblk.multiCMD, "run_command", fake_run_command)
    cut = []
    rows = statblk.get_drives_info(output="NAME,SIZE,MOUNTPOINT", timeout=2, cut=cut)
    assert cut == expected
    assert [r[0] for r in rows[1:]] == ["disk3", "disk3s1"]  # disk3, unmounted, has its diskutil size


def test_a_silent_diskutil_and_mount_are_stopped_and_recorded(monkeypatch, tmp_path):
    # Through the real multiCMD: each prints its first line, then nothing, as a diskutil or mount stuck on a
    # device does. Their first lines are still read.
    def silent(name, first_line):
        path = tmp_path / name
        path.write_text("#!/bin/sh\necho '%s'\nexec sleep 30\n" % first_line)
        path.chmod(0o755)
        return str(path)

    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", silent("diskutil", "Device Node: /dev/disk3s1"))
    silent("mount", DARWIN_MOUNT_SAMPLE[0])
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ.get("PATH", ""))
    cut = []
    start = time.monotonic()
    # 0.3 s because the first line is read before the stop in 30 of 30 runs at 0.02 s (Python 3.6 and 3.11, load
    # average 13 to 40 on 32 cores, 2026-11-15), so it is 15 times what the test needs.
    info = statblk.get_macos_diskutil_info(timeout=0.3, cut=cut)
    mounts = statblk.parseMount(0.3, cut=cut)
    assert time.monotonic() - start < 10
    assert cut == ["diskutil", "mount"]
    assert "/dev/disk3s1" in info and "/dev/disk3s1" in mounts


# The row rule: a filter drops a row only on a value that was read.

@pytest.mark.parametrize("output, diskutil", [
    ("NAME,MOUNTPOINT", (MACOS26_DISKUTIL, 0)),  # no diskutil column: diskutil does not run
    ("NAME,SIZE,MOUNTPOINT", (BEFORE_DISK1, 124)),  # stopped before disk1
])
def test_darwin_device_with_no_size_read_stays_with_a_blank_size(monkeypatch, output, diskutil):
    _darwin_machine(monkeypatch, diskutil=diskutil)
    rows = statblk.get_drives_info(output=output, timeout=2)
    assert _names(rows) == ALL_NAMES
    if "SIZE" in output:
        assert ["disk0", "500277792768B", ""] in rows and ["disk3", "", ""] in rows


@pytest.mark.parametrize("show_zero, listed", [(False, False), (True, True)])
def test_darwin_size_read_as_zero_drops_the_row(monkeypatch, show_zero, listed):
    zero = [line.replace("(500277792768 Bytes)", "(0 Bytes)") if "(500277792768 Bytes)" in line else line
            for line in MACOS26_DISKUTIL]
    _darwin_machine(monkeypatch, diskutil=(zero, 0))
    rows = statblk.get_drives_info(output="NAME,SIZE", show_zero_size_devices=show_zero, timeout=2)
    assert (["disk0", "0B"] in rows) == listed
    assert ("disk0" in _names(rows)) == listed


@pytest.mark.parametrize("mount, diskutil, kept", [
    ((MACOS26_MOUNT, 0), (MACOS26_DISKUTIL, 0), []),  # both answered: the devices diskutil gives no type go
    ((MACOS26_MOUNT, 0), (BEFORE_DISK1, 124), UNMOUNTED),  # diskutil stopped
    ((MACOS26_MOUNT, 0), ([], 127), UNMOUNTED),  # no diskutil answer at all
    ((MACOS26_MOUNT[:2], 124), (MACOS26_DISKUTIL, 0), UNMOUNTED),  # mount stopped
])
def test_darwin_formated_only_drops_only_a_type_read_as_blank(monkeypatch, mount, diskutil, kept):
    _darwin_machine(monkeypatch, mount=mount, diskutil=diskutil)
    rows = statblk.get_drives_info(output="NAME,FSTYPE", formated_only=True, timeout=2)
    typeless = ["disk0", "disk0s1", "disk0s2", "disk0s3", "disk1", "disk2", "disk3"]  # no File System Personality
    assert [name for name in _names(rows) if name in typeless] == [name for name in kept if name in typeless]
    assert "disk3s5" in _names(rows)


def test_darwin_formated_only_keeps_a_device_diskutil_did_not_describe(monkeypatch):
    _darwin_machine(monkeypatch, dev=MACOS26_DEV + ["/dev/disk4"])
    rows = statblk.get_drives_info(output="NAME,FSTYPE", formated_only=True, timeout=2)
    assert ["disk4", ""] in rows and "disk0" not in _names(rows)


def test_darwin_active_only_drops_nothing(monkeypatch):
    # macOS has no per-device throughput to read: READ and WRITE show 0, which is not "idle".
    _darwin_machine(monkeypatch)
    rows = statblk.get_drives_info(output="NAME,READ", active_only=True, pseudo=True, timeout=2)
    assert _names(rows)[:len(ALL_NAMES)] == ALL_NAMES and "devfs" in _names(rows)
