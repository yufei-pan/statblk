from types import SimpleNamespace

import pytest

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
    assert second == (None, None)  # not read: not idle
    # Third next should again be a single short-line yield, not a double IndexError path
    third = next(it)
    assert third == (None, None)
    assert reads["n"] == 3


def test_unreadable_stat_is_not_read_not_idle(tmp_path, monkeypatch):
    # A stat that cannot be read (the device vanished after the listing) gives no throughput: (None, None), which -A
    # does not take for an idle device. 1.63 yielded (0, 0).
    block = make_sysfs_block(tmp_path, "sda", size_sectors=10)  # no stat file
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    it = statblk.get_read_write_rate_throughput_iter(str(block))
    assert next(it) == (None, None) and next(it) == (None, None)
    assert next(statblk.get_read_write_rate_throughput_iter(str(tmp_path / "gone"))) == (None, None)


def test_rate_after_a_sample_that_was_not_read_counts_from_the_last_one_read(tmp_path, monkeypatch):
    # The first sample read is the since-boot average, whatever came before it; later ones count from the last sample
    # read, not from zero (1.63 read the bytes since boot over one interval after a first read that failed).
    block = make_sysfs_block(tmp_path, "sda", size_sectors=10)
    stat = block / "stat"
    clock = iter([100.0, 102.0])
    monkeypatch.setattr(statblk, "time", SimpleNamespace(monotonic=lambda: next(clock)))
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    it = statblk.get_read_write_rate_throughput_iter(str(block))
    assert next(it) == (None, None)
    stat.write_text("0 0 2000 1000 0 0 4000 2000 0 0 0\n")  # 1 MiB read in 1 s busy, 2 MiB written in 2 s
    assert next(it) == (2000 * 512, 4000 * 512 // 2)
    stat.write_text("0 0 6000 1000 0 0 4000 2000 0 0 0\n")  # 2 s later: 4000 sectors more read
    assert next(it) == (4000 * 512 // 2, 0)


@pytest.mark.parametrize("read_after, written_after, expected", [
    (1000, 4000 + 2000, (None, 2000 * 512 // 2)),  # the read counter went back (2000 to 1000): READ blank, WRITE live
    (1000, 1000, (None, None)),  # both reset: the device was removed and added again under its name
], ids=["read counter went back", "device re-added"])
def test_counter_reset_between_samples_has_no_rate_for_that_interval(tmp_path, monkeypatch, read_after,
                                                                       written_after, expected):
    # A counter below the last sample's was reset in between: what the interval moved is not known, so that
    # direction's rate is None (blank, null in -J), not negative as in 1.64; the next interval counts from the reset.
    block = make_sysfs_block(tmp_path, "sda", size_sectors=10)
    stat = block / "stat"
    clock = iter([100.0, 102.0, 104.0])
    monkeypatch.setattr(statblk, "time", SimpleNamespace(monotonic=lambda: next(clock)))
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    it = statblk.get_read_write_rate_throughput_iter(str(block))
    stat.write_text("0 0 2000 1000 0 0 4000 2000 0 0 0\n")
    assert next(it) == (2000 * 512, 4000 * 512 // 2)  # the since-boot average
    stat.write_text("0 0 %d 1000 0 0 %d 2000 0 0 0\n" % (read_after, written_after))
    assert next(it) == expected
    stat.write_text("0 0 %d 1000 0 0 %d 2000 0 0 0\n" % (read_after + 400, written_after + 800))
    assert next(it) == (400 * 512 // 2, 800 * 512 // 2)
