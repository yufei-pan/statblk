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
