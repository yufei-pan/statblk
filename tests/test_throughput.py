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
