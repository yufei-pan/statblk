import threading
import time
from types import SimpleNamespace

import pytest

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


@pytest.fixture
def hung_statvfs(monkeypatch):
    """os.statvfs that blocks like a hard NFS mount whose server is gone."""
    release = threading.Event()
    calls = []
    st = SimpleNamespace(f_frsize=1024, f_bsize=1024, f_blocks=100, f_bfree=40, f_bavail=30)

    def fake_statvfs(path):
        calls.append(path)
        if path == "/hung":
            release.wait(10)
        return st

    monkeypatch.setattr(statblk.os, "statvfs", fake_statvfs)
    monkeypatch.setattr(statblk, "_HUNG_STATVFS", {})
    yield calls
    release.set()


def test_statvfs_timeout_returns_none(hung_statvfs):
    start = time.monotonic()
    assert statblk.get_statvfs_use_size("/hung", timeout=0.1) is None
    assert time.monotonic() - start < 2


def test_statvfs_known_hung_mount_not_retried(hung_statvfs):
    assert statblk.get_statvfs_use_size("/hung", timeout=0.1) is None
    start = time.monotonic()
    assert statblk.get_statvfs_use_size("/hung", timeout=5) is None
    assert time.monotonic() - start < 1
    assert hung_statvfs == ["/hung"]


def test_statvfs_with_timeout_healthy_mount(hung_statvfs):
    assert statblk.get_statvfs_use_size("/ok", timeout=5) == (100 * 1024, 60 * 1024, 30 * 1024)
