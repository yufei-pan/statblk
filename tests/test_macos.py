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


MOUNT = "/sbin/mount"  # where macOS keeps it


def _darwin_commands(monkeypatch):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")
    monkeypatch.setattr(statblk, "MOUNT_PATH", MOUNT)


def _diskutil_info(monkeypatch, lines, returncode=0):
    _darwin_commands(monkeypatch)
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
    ("   Disk Size:                 Not applicable (no media)", 0),  # an empty slot, as 1.62 read it
    ("   Disk Size:                 Not applicable (no file system)", None),  # no other "Not applicable" is a size
    (None, None),  # diskutil was stopped before the line, or never prints it
], ids=["zero bytes", "no media", "other not applicable", "no line"])
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
    _darwin_commands(monkeypatch)
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", None)
    _fake_dev_listing(monkeypatch, [d[len("/dev/"):] for d in dev])
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p in dev)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    monkeypatch.setattr(statblk.multiCMD, "run_command",
                        lambda command, **k: FakeCmdResult(*(mount if command == MOUNT else diskutil)))


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


def test_throughput_not_read_on_darwin(monkeypatch):
    # macOS has no per-device throughput to read: READ and WRITE are blank, not a 0 B/s statblk never measured.
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    it = statblk.get_read_write_rate_throughput_iter("/dev/disk0")
    assert next(it) == (None, None)


def test_darwin_read_and_write_are_blank_and_null(monkeypatch):
    _darwin_machine(monkeypatch)
    rows = statblk.get_drives_info(output="NAME,READ,WRITE", timeout=2, print_bytes=True)
    assert _names(rows) == ALL_NAMES and {(r[1], r[2]) for r in rows[1:]} == {("", "")}
    assert {(o["READ"], o["WRITE"]) for o in statblk.rows_to_objects(rows)} == {(None, None)}


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
    monkeypatch.setattr(statblk, "parseMount", lambda timeout=0, unanswered=None: mounts)
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
    monkeypatch.setattr(statblk, "parseMount", lambda timeout=0, unanswered=None: defaultdict(list))
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    info = {
        "/dev/disk4s1": {"SIZE_BYTES": 1000, "FSTYPE": "ExFAT"},
        "/dev/disk4s2": {"SIZE_BYTES": 2000, "FSTYPE": ""},
    }
    monkeypatch.setattr(statblk, "get_macos_diskutil_info", lambda timeout=0, unanswered=None: info)
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
    _darwin_commands(monkeypatch)
    _fake_dev_listing(monkeypatch, ["disk3", "disk3s1"])
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    calls = {}

    def fake_run_command(command, timeout=0, **kwargs):
        calls[command.split()[0].rsplit("/", 1)[-1]] = timeout
        if command == MOUNT:
            return FakeCmdResult(DARWIN_MOUNT_SAMPLE)
        return FakeCmdResult(MACOS26_DISKUTIL)

    monkeypatch.setattr(statblk.multiCMD, "run_command", fake_run_command)
    statblk.get_drives_info(output="NAME,SIZE,MOUNTPOINT", timeout=timeout)
    assert calls == {"diskutil": expected, "mount": expected}


@pytest.mark.parametrize("returncode", [124, 0, 1, 127], ids=["stopped", "answered", "failed", "not found"])
def test_diskutil_and_mount_that_did_not_answer_are_recorded(monkeypatch, returncode):
    # 124 is multiCMD's return code for a command it stopped at the timeout, 127 for one it did not find; what a
    # command printed before is still read.
    _darwin_commands(monkeypatch)

    def fake_run_command(command, timeout=0, **kwargs):
        if command == MOUNT:
            return FakeCmdResult(DARWIN_MOUNT_SAMPLE, returncode)
        return FakeCmdResult(MACOS26_DISKUTIL, returncode)

    monkeypatch.setattr(statblk.multiCMD, "run_command", fake_run_command)
    unanswered = {}
    assert "/dev/disk3s1" in statblk.get_macos_diskutil_info(timeout=1, unanswered=unanswered)
    assert list(statblk.parseMount(1, unanswered=unanswered)) == ["/dev/disk3s1"]
    assert unanswered == ({} if returncode == 0 else {"diskutil": returncode, "mount": returncode})


@pytest.mark.parametrize("returncode, expected", [(124, ["diskutil", "mount"]), (0, []), (1, [])])
def test_get_drives_info_records_diskutil_and_mount(monkeypatch, returncode, expected):
    # The whole path: what main() prints and decides from comes through get_drives_info's own record; its `cut` list
    # (1.62) still gets what the timeout stopped.
    _darwin_commands(monkeypatch)
    _fake_dev_listing(monkeypatch, ["disk3", "disk3s1"])
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))

    def fake_run_command(command, timeout=0, **kwargs):
        if command == MOUNT:
            return FakeCmdResult(DARWIN_MOUNT_SAMPLE, returncode)
        return FakeCmdResult(MACOS26_DISKUTIL, returncode)

    monkeypatch.setattr(statblk.multiCMD, "run_command", fake_run_command)
    cut, unanswered = [], {}
    rows = statblk.get_drives_info(output="NAME,SIZE,MOUNTPOINT", timeout=2, cut=cut, unanswered=unanswered)
    assert cut == expected
    assert unanswered == ({} if returncode == 0 else {"diskutil": returncode, "mount": returncode})
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
    monkeypatch.setattr(statblk, "MOUNT_PATH", silent("mount", DARWIN_MOUNT_SAMPLE[0]))
    unanswered = {}
    start = time.monotonic()
    # 0.3 s because the first line is read before the stop in 30 of 30 runs at 0.02 s (Python 3.6 and 3.11, load
    # average 13 to 40 on 32 cores, 2026-11-15), so it is 15 times what the test needs.
    info = statblk.get_macos_diskutil_info(timeout=0.3, unanswered=unanswered)
    mounts = statblk.parseMount(0.3, unanswered=unanswered)
    assert time.monotonic() - start < 10
    assert unanswered == {"diskutil": 124, "mount": 124}
    assert "/dev/disk3s1" in info and "/dev/disk3s1" in mounts


def test_a_missing_diskutil_and_mount_are_recorded_as_not_found(monkeypatch, tmp_path):
    # Through the real multiCMD: a command it cannot find answers 127 (cron's PATH on macOS, /usr/bin:/bin, has
    # neither /usr/sbin/diskutil nor /sbin/mount; statblk looks in the sbin directories too, see find_command).
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", str(tmp_path / "diskutil"))
    monkeypatch.setattr(statblk, "MOUNT_PATH", str(tmp_path / "mount"))
    unanswered = {}
    assert statblk.get_macos_diskutil_info(timeout=2, unanswered=unanswered) == {}
    assert statblk.parseMount(2, unanswered=unanswered) == {}
    assert unanswered == {"diskutil": 127, "mount": 127}


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


@pytest.mark.parametrize("returncode, listed", [(0, False), (1, True), (124, True)])
def test_darwin_formated_only_keeps_a_device_whose_type_line_diskutil_did_not_reach(monkeypatch, returncode, listed):
    # diskutil's output ends right after disk3s1's Device Node, before its File System Personality: a diskutil that
    # exited 0 answered in full, so that blank type is read; one that failed or was stopped did not.
    cut_at = MACOS26_DISKUTIL.index("   Device Node:               /dev/disk3s1") + 1
    _darwin_machine(monkeypatch, diskutil=(MACOS26_DISKUTIL[:cut_at], returncode))
    rows = statblk.get_drives_info(output="NAME,FSTYPE", formated_only=True, timeout=2)
    assert ("disk3s1" in _names(rows)) == listed


@pytest.mark.parametrize("show_zero, listed", [(False, False), (True, True)])
def test_darwin_empty_slot_is_a_zero_size_device(monkeypatch, show_zero, listed):
    # "Disk Size: Not applicable (no media)" reads as 0, as in 1.62: hidden by default, like any zero-size device.
    slot = ["", "   Device Identifier:         disk9", "   Device Node:               /dev/disk9", "",
            "   Disk Size:                 Not applicable (no media)", "   Solid State:               No"]
    _darwin_machine(monkeypatch, dev=MACOS26_DEV + ["/dev/disk9"], diskutil=(MACOS26_DISKUTIL + slot, 0))
    rows = statblk.get_drives_info(output="NAME,SIZE", show_zero_size_devices=show_zero, timeout=2)
    assert (["disk9", "0B"] in rows) == listed


def test_darwin_formated_only_keeps_a_device_diskutil_did_not_describe(monkeypatch):
    _darwin_machine(monkeypatch, dev=MACOS26_DEV + ["/dev/disk4"])
    rows = statblk.get_drives_info(output="NAME,FSTYPE", formated_only=True, timeout=2)
    assert ["disk4", ""] in rows and "disk0" not in _names(rows)


def test_darwin_active_only_drops_nothing(monkeypatch):
    # macOS has no per-device throughput to read: READ and WRITE show 0, which is not "idle".
    _darwin_machine(monkeypatch)
    rows = statblk.get_drives_info(output="NAME,READ", active_only=True, pseudo=True, timeout=2)
    assert _names(rows)[:len(ALL_NAMES)] == ALL_NAMES and "devfs" in _names(rows)
