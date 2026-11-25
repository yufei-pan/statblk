import os
from collections import defaultdict

import pytest

import statblk
from fakes import FakeCmdResult, make_sysfs_block, redirect_sys_class_block
from test_drives_info import _patch_linux_basics, _patch_multicmd

REAL_GET_PARTITION_PARENT_NAME = statblk.get_partition_parent_name  # _patch_linux_basics replaces it


def test_read_size_uses_512(tmp_path):
    block = make_sysfs_block(tmp_path, "sda", size_sectors=2048, hw_sector_size=4096)
    assert statblk.read_size(str(block)) == 2048 * 512


def test_read_size_none_when_it_cannot_be_read(tmp_path):
    # A device that vanished between the listing and the read: no size was read, which is not a size of 0.
    block = make_sysfs_block(tmp_path, "sda", size_sectors=2048)
    (block / "size").unlink()
    assert statblk.read_size(str(block)) is None
    assert statblk.read_size(str(tmp_path / "gone")) is None
    (block / "size").write_text("0\n")
    assert statblk.read_size(str(block)) == 0


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


def test_get_partition_parent_name_disk_vs_partition(tmp_path, monkeypatch):
    """Linux: whole disk returns /dev/<name>; partition resolves parent via realpath nest."""
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    make_sysfs_block(tmp_path, "sda", size_sectors=100)

    # Real sysfs: class/block/sda1 -> .../block/sda/sda1 (parent dir name = sda)
    disk_real = tmp_path / "sys" / "devices" / "virtual" / "block" / "sda"
    part_real = disk_real / "sda1"
    part_real.mkdir(parents=True)
    (part_real / "partition").write_text("1")
    (part_real / "size").write_text("10")
    class_block = tmp_path / "sys" / "class" / "block"
    (class_block / "sda1").symlink_to(os.path.relpath(part_real, class_block))

    redirect_sys_class_block(tmp_path, monkeypatch)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p == "/dev/sda")

    assert statblk.get_partition_parent_name("sda") == "/dev/sda"
    assert statblk.get_partition_parent_name("sda1") == "/dev/sda"
    assert statblk.get_partition_parent_name("/dev/sda1") == "/dev/sda"


def _make_sysfs_host(tmp_path):
    """A fake /sys/class/block as the kernel lays it out: the hardware disk sda (a `device` link) with partitions sda1 and
    sda2, and the virtual loop0 (no `device` link) with loop0p1; a partition's class entry links to a directory nested
    under its disk's, which is where the real get_partition_parent_name() reads the disk from."""
    class_block = tmp_path / "sys" / "class" / "block"
    for disk, with_device, parts in (("sda", True, ("sda1", "sda2")), ("loop0", False, ("loop0p1",))):
        make_sysfs_block(tmp_path, disk, size_sectors=100, with_device=with_device)
        for part in parts:
            part_real = tmp_path / "sys" / "devices" / "virtual" / "block" / disk / part
            part_real.mkdir(parents=True)
            (part_real / "partition").write_text("1")
            (class_block / part).symlink_to(os.path.relpath(part_real, class_block))


def test_has_sysfs_device_and_the_parent_of_a_partition_with_no_dev_node(tmp_path, monkeypatch):
    # the container's view: sysfs lists the devices, /dev has no node for any of them
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    _make_sysfs_host(tmp_path)
    redirect_sys_class_block(tmp_path, monkeypatch)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: False)
    assert statblk.has_sysfs_device("/dev/sda") and not statblk.has_sysfs_device("/dev/loop0")
    assert not statblk.has_sysfs_device("/dev/sda1")  # a partition has no `device` link: its disk's decides
    assert statblk.get_partition_parent_name("/dev/sda1") == "/dev/sda"
    assert statblk.get_partition_parent_name("/dev/loop0p1") == "/dev/loop0"
    assert statblk.get_partition_parent_name("/dev/sda") is None  # a whole disk's own node is not there


@pytest.mark.parametrize("nodes, expected", [
    ((), {"sda": "UNKNOWN", "sda1": "UNKNOWN", "sda2": "UNKNOWN", "loop0": "", "loop0p1": ""}),
    (("/dev/sda",), {"sda": "OK", "sda1": "OK", "sda2": "OK", "loop0": "", "loop0p1": ""}),
], ids=["no node", "the disk's node"])
def test_smart_of_a_partition_with_no_dev_node_follows_its_disk_through_sysfs(tmp_path, monkeypatch, nodes, expected):
    # The real has_sysfs_device() and get_partition_parent_name() on a fake sysfs tree: a partition that no longer traced
    # to its disk would read blank (a partition has no `device` link), which --check counts as healthy.
    _make_sysfs_host(tmp_path)
    devices = ["/dev/sda", "/dev/sda1", "/dev/sda2", "/dev/loop0", "/dev/loop0p1"]
    _patch_linux_basics(monkeypatch, devices=devices, mounts=defaultdict(list))
    monkeypatch.setattr(statblk, "get_partition_parent_name", REAL_GET_PARTITION_PARENT_NAME)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p in nodes)
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", "/usr/sbin/smartctl")
    redirect_sys_class_block(tmp_path, monkeypatch)
    _patch_multicmd(monkeypatch, FakeCmdResult(["SMART Health Status: OK"]))
    rows = statblk.get_drives_info(output="NAME,SMART", timeout=2)
    assert dict((r[0], r[1]) for r in rows[1:]) == expected


def _make_executable(path):
    path.write_text("#!/bin/sh\n")
    path.chmod(0o755)
    return path


def test_find_command_falls_back_to_sbin_dirs(tmp_path, monkeypatch):
    # Debian's non-root PATH omits /usr/sbin where smartmontools installs, and macOS cron's PATH (/usr/bin:/bin) omits
    # /usr/sbin/diskutil and /sbin/mount.
    user_bin = tmp_path / "bin"
    user_bin.mkdir()
    sbin = tmp_path / "sbin"
    sbin.mkdir()
    smartctl = _make_executable(sbin / "smartctl")
    monkeypatch.setenv("PATH", str(user_bin))
    assert statblk.find_command("smartctl", fallback_dirs=[str(sbin)]) == str(smartctl)


def test_find_command_default_fallback_is_the_sbin_dirs():
    # DISKUTIL_PATH and MOUNT_PATH rely on the default under macOS cron's PATH; the default is bound when the function
    # is defined, so it can't be monkeypatched.
    assert {"/usr/sbin", "/sbin"} <= set(statblk.SBIN_DIRS)
    assert statblk.find_command.__defaults__ == (statblk.SBIN_DIRS,)


def test_find_command_prefers_path(tmp_path, monkeypatch):
    user_bin = tmp_path / "bin"
    user_bin.mkdir()
    on_path = _make_executable(user_bin / "smartctl")
    sbin = tmp_path / "sbin"
    sbin.mkdir()
    _make_executable(sbin / "smartctl")
    monkeypatch.setenv("PATH", str(user_bin))
    assert statblk.find_command("smartctl", fallback_dirs=[str(sbin)]) == str(on_path)


def test_find_command_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    assert statblk.find_command("smartctl", fallback_dirs=[str(tmp_path)]) is None
