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


def test_statvfs_thread_starts_without_threading_start(monkeypatch, hung_statvfs):
    # threading.Thread.start() on the main thread takes threading's _active_limbo_lock and waits on an Event: a
    # Ctrl-C landing there can leave the lock held, and Python 3.6's exit then waits for it for good (`statblk -w`
    # stopped with Ctrl-C hung). The statvfs thread is started by one C call instead.
    def start(self):
        raise AssertionError("threading.Thread.start() called")

    monkeypatch.setattr(threading.Thread, "start", start)
    assert statblk.get_statvfs_use_size("/ok", timeout=5) == (100 * 1024, 60 * 1024, 30 * 1024)
    assert statblk.get_statvfs_use_size("/hung", timeout=0.1) is None
    assert statblk.get_statvfs_use_size("/hung", timeout=0.1) is None
    assert hung_statvfs == ["/ok", "/hung"]


def test_statvfs_of_a_mount_that_answers_again_is_asked_again(monkeypatch):
    # Kept behaviour (1.61 did the same): once the stuck call returns, the next refresh asks the mount again.
    release = threading.Event()
    calls = []
    st = SimpleNamespace(f_frsize=1024, f_bsize=1024, f_blocks=100, f_bfree=40, f_bavail=30)

    def fake_statvfs(path):
        calls.append(path)
        if len(calls) == 1:
            release.wait(10)
        return st

    monkeypatch.setattr(statblk.os, "statvfs", fake_statvfs)
    monkeypatch.setattr(statblk, "_HUNG_STATVFS", {})
    try:
        assert statblk.get_statvfs_use_size("/nfs", timeout=0.1) is None
        assert statblk.get_statvfs_use_size("/nfs", timeout=5) is None  # still stuck: not asked again
    finally:
        release.set()  # a failed assertion must not leave the stuck thread waiting its 10 s
    deadline = time.monotonic() + 5
    usage = None
    while usage is None and time.monotonic() < deadline:
        time.sleep(0.01)
        usage = statblk.get_statvfs_use_size("/nfs", timeout=5)
    assert usage == (100 * 1024, 60 * 1024, 30 * 1024)
    assert calls == ["/nfs", "/nfs"]
