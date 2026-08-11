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
