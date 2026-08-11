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
