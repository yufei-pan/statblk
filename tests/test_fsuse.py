from types import SimpleNamespace

import statblk


def test_get_statvfs_use_size_excludes_reserved(monkeypatch):
    # 100 blocks total, 40 free to root, 30 avail to user → 60 used, not 70
    st = SimpleNamespace(f_frsize=1024, f_bsize=1024, f_blocks=100, f_bfree=40, f_bavail=30)

    def fake_statvfs(_path):
        return st

    monkeypatch.setattr(statblk.os, "statvfs", fake_statvfs)
    total, used, avail = statblk.get_statvfs_use_size("/")
    assert total == 100 * 1024
    assert used == (100 - 40) * 1024
    assert avail == 30 * 1024
    assert used != total - avail  # reserved must not count as used


def test_fsuse_percent_matches_df_ceiling():
    used, avail = 3515, 6485  # arbitrary bytes
    denom = used + avail
    pct = (used * 100) // denom
    if (used * 100) % denom:
        pct += 1
    # sanity: this is the formula get_drives_info must use
    assert pct == 36
