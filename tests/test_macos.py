import os
from collections import defaultdict

import pytest

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
    monkeypatch.setattr(statblk, "parseMount", lambda: mounts)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    assert rows[1:] == [["disk3s1s1", "/"]]


@pytest.mark.parametrize("output", ["NAME,SIZE", "NAME,MOUNTPOINT"])
def test_darwin_formated_only_without_fstype_column(monkeypatch, output):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    _fake_dev_listing(monkeypatch, ["disk4s1", "disk4s2"])
    monkeypatch.setattr(statblk, "parseMount", lambda: defaultdict(list))
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    info = {
        "/dev/disk4s1": {"SIZE_BYTES": 1000, "FSTYPE": "ExFAT"},
        "/dev/disk4s2": {"SIZE_BYTES": 2000, "FSTYPE": ""},
    }
    monkeypatch.setattr(statblk, "get_macos_diskutil_info", lambda timeout=4: info)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output=output, formated_only=True, timeout=2)
    assert [r[0] for r in rows[1:]] == ["disk4s1"]
