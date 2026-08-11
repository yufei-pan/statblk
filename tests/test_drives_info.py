from collections import defaultdict

import statblk
from fakes import FakeCmdResult


def _mount_table(device="/dev/sda1", mp="/data"):
    return defaultdict(list, {device: [statblk.MountEntry(mp, "ext4", ["rw"])]})


def _patch_linux_basics(monkeypatch, devices=None, mounts=None):
    devices = devices or ["/dev/sda1"]
    mounts = mounts if mounts is not None else _mount_table()
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    monkeypatch.setattr(statblk, "get_blocks", lambda: list(devices))
    monkeypatch.setattr(statblk, "parseMount", lambda: mounts)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_partition_parent_name", lambda p: "/dev/sda")
    monkeypatch.setattr(statblk, "lsblk_supports_pairs", lambda: True)
    monkeypatch.setattr(
        statblk,
        "get_statvfs_use_size",
        lambda mp: (1000, 350, 650),  # total, used, avail → 35% ceil? 3500/1000=35 exact
    )
    # throughput: finite then zeros
    def fake_tpt(_path):
        yield 100, 200
        while True:
            yield 0, 0

    monkeypatch.setattr(statblk, "get_read_write_rate_throughput_iter", fake_tpt)


def test_output_and_exclude_columns(monkeypatch):
    _patch_linux_basics(monkeypatch)
    fake = FakeCmdResult(
        ['NAME="/dev/sda1" SIZE="1000" FSTYPE="ext4" UUID="u" LABEL="L"'], 0
    )
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output="NAME,FSUSE%,MOUNTPOINT", exclude="FSUSE%", timeout=2)
    assert rows[0] == ["NAME", "MOUNTPOINT"]


def test_filter_and_invert(monkeypatch):
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1", "/dev/nvme0n1"])
    mounts = _mount_table("/dev/sda1", "/")
    mounts["/dev/nvme0n1"] = [statblk.MountEntry("/mnt", "xfs", ["rw"])]
    monkeypatch.setattr(statblk, "parseMount", lambda: mounts)
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output="NAME,MOUNTPOINT", filter_patterns=["nvme"], timeout=2)
    names = [r[0] for r in rows[1:]]
    assert any("nvme" in n for n in names)
    assert not any(n.endswith("sda1") or n == "sda1" for n in names)


def test_lsblk_join_uses_timeout(monkeypatch):
    _patch_linux_basics(monkeypatch)
    fake = FakeCmdResult(
        ['NAME="/dev/sda1" SIZE="1000" FSTYPE="ext4" UUID="u" LABEL="L"'], 0
    )
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    statblk.get_drives_info(output="NAME,SIZE,UUID,LABEL,FSTYPE", timeout=7)
    assert fake.join_timeouts == [7]


def test_cache_cleared_between_get_drives_info_calls(monkeypatch):
    _patch_linux_basics(monkeypatch)
    calls = {"n": 0}
    tables = [
        _mount_table("/dev/sda1", "/old"),
        _mount_table("/dev/sda1", "/new"),
    ]

    def parse_mount():
        # emulate cache decorator miss after clear: return next table
        idx = min(calls["n"], len(tables) - 1)
        calls["n"] += 1
        return tables[idx]

    # Replace cached parseMount with counting function; get_drives_info still calls cache_clear on attribute if present
    parse_mount.cache_clear = lambda: None
    monkeypatch.setattr(statblk, "parseMount", parse_mount)
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    r1 = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    r2 = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    assert any("/old" in row for row in r1)
    assert any("/new" in row for row in r2)
    assert calls["n"] >= 2


def test_mounted_only_skips_unmounted(monkeypatch):
    mounts = _mount_table("/dev/sda1", "/")
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1", "/dev/sda2"], mounts=mounts)
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    # Unmounted sda2 needs a non-zero size path when mounted_only=False; with
    # mounted_only=True it is skipped before size lookup.
    monkeypatch.setattr(statblk, "read_size", lambda p: 1000)
    rows = statblk.get_drives_info(
        output="NAME,MOUNTPOINT", mounted_only=True, full=True, timeout=2
    )
    assert [r[0] for r in rows[1:]] == ["/dev/sda1"]


def test_best_only_picks_shortest_mount(monkeypatch):
    mounts = defaultdict(
        list,
        {
            "/dev/sda1": [
                statblk.MountEntry("/data/long/path", "ext4", ["rw"]),
                statblk.MountEntry("/data", "ext4", ["rw"]),
            ]
        },
    )
    _patch_linux_basics(monkeypatch, mounts=mounts)
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows_all = statblk.get_drives_info(output="NAME,MOUNTPOINT", best_only=False, timeout=2)
    assert sorted(r[1] for r in rows_all[1:]) == ["/data", "/data/long/path"]
    rows_best = statblk.get_drives_info(output="NAME,MOUNTPOINT", best_only=True, timeout=2)
    assert len(rows_best) == 2
    assert rows_best[1][1] == "/data"


def test_show_zero_size_devices(monkeypatch):
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1"], mounts=defaultdict(list))
    fake = FakeCmdResult(
        ['NAME="/dev/sda1" SIZE="0" FSTYPE="" UUID="" LABEL=""'], 0
    )
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    hidden = statblk.get_drives_info(
        output="NAME,SIZE", show_zero_size_devices=False, timeout=2
    )
    assert len(hidden) == 1
    shown = statblk.get_drives_info(
        output="NAME,SIZE", show_zero_size_devices=True, timeout=2
    )
    assert len(shown) == 2
    assert shown[1][0] == "sda1"
    assert shown[1][1] == "0B"


def test_match_devname_only(monkeypatch):
    mounts = defaultdict(
        list,
        {
            "/dev/sda1": [statblk.MountEntry("/mnt/nvme-backup", "ext4", ["rw"])],
            "/dev/nvme0n1": [statblk.MountEntry("/", "xfs", ["rw"])],
        },
    )
    _patch_linux_basics(
        monkeypatch, devices=["/dev/sda1", "/dev/nvme0n1"], mounts=mounts
    )
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    # Full-row filter: mountpoint /mnt/nvme-backup matches "nvme" too.
    rows_any = statblk.get_drives_info(
        output="NAME,MOUNTPOINT", filter_patterns=["nvme"], timeout=2
    )
    names_any = [r[0] for r in rows_any[1:]]
    assert "sda1" in names_any and "nvme0n1" in names_any
    # Device-name-only: only /dev/nvme0n1 matches.
    rows_dev = statblk.get_drives_info(
        output="NAME,MOUNTPOINT",
        filter_patterns=["nvme"],
        match_devname_only=True,
        timeout=2,
    )
    assert [r[0] for r in rows_dev[1:]] == ["nvme0n1"]


def test_formated_only(monkeypatch):
    _patch_linux_basics(
        monkeypatch, devices=["/dev/sda1", "/dev/sda2"], mounts=defaultdict(list)
    )
    fake = FakeCmdResult(
        [
            'NAME="/dev/sda1" SIZE="1000" FSTYPE="ext4" UUID="u" LABEL="L"',
            'NAME="/dev/sda2" SIZE="2000" FSTYPE="" UUID="" LABEL=""',
        ],
        0,
    )
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(
        output="NAME,FSTYPE,SIZE", formated_only=True, timeout=2
    )
    assert [r[0] for r in rows[1:]] == ["sda1"]
    assert rows[1][1] == "ext4"


def test_pseudo_adds_mount_table_keys(monkeypatch):
    mounts = defaultdict(
        list,
        {
            "/dev/sda1": [statblk.MountEntry("/data", "ext4", ["rw"])],
            "tmpfs": [statblk.MountEntry("/tmp", "tmpfs", ["rw"])],
        },
    )
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1"], mounts=mounts)
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p.startswith("/dev/"))
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    without = statblk.get_drives_info(
        output="NAME,MOUNTPOINT", pseudo=False, timeout=2
    )
    assert [r[0] for r in without[1:]] == ["sda1"]
    with_pseudo = statblk.get_drives_info(
        output="NAME,MOUNTPOINT", pseudo=True, timeout=2
    )
    names = [r[0] for r in with_pseudo[1:]]
    assert "sda1" in names and "tmpfs" in names
    assert any(r[1] == "/tmp" for r in with_pseudo[1:])


def test_smart_join_uses_timeout(monkeypatch):
    _patch_linux_basics(monkeypatch)
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", "/usr/sbin/smartctl")
    smart = FakeCmdResult(
        ["SMART overall-health self-assessment test result: PASSED"], 0
    )
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: smart)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(output="NAME,SMART", timeout=9)
    assert smart.join_timeouts == [9]
    assert rows[1][0] == "sda1"
    assert rows[1][1] == "OK"
