import os

import statblk
from fakes import make_sysfs_block


def _redirect_sys_class_block(tmp_path, monkeypatch):
    """Point hardcoded /sys/class/block joins at tmp_path/sys/class/block."""
    fake = str(tmp_path / "sys" / "class" / "block")
    real_join = os.path.join

    def join(a, *parts):
        if a == "/sys/class/block":
            return real_join(fake, *parts)
        return real_join(a, *parts)

    monkeypatch.setattr(os.path, "join", join)


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

    _redirect_sys_class_block(tmp_path, monkeypatch)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p == "/dev/sda")
    for fn in (statblk.get_partition_parent_name, statblk.is_block_device):
        clear = getattr(fn, "cache_clear", None)
        if clear:
            clear()

    assert statblk.get_partition_parent_name("sda") == "/dev/sda"
    assert statblk.get_partition_parent_name("sda1") == "/dev/sda"
    assert statblk.get_partition_parent_name("/dev/sda1") == "/dev/sda"
