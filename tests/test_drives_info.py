from collections import defaultdict

import statblk
from fakes import FakeCmdResult, make_sysfs_block, redirect_sys_class_block

REAL_READ_DISCARD_SUPPORT = statblk.read_discard_support
REAL_READ_MODEL_AND_SERIAL = statblk.read_model_and_serial
REAL_PARSE_MOUNT = statblk.parseMount


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
    monkeypatch.setattr(
        statblk,
        "get_statvfs_use_size",
        lambda mp, timeout=None: (1000, 350, 650),  # total, used, avail → 35% ceil? 3500/1000=35 exact
    )
    # throughput: finite then zeros
    def fake_tpt(_path):
        yield 100, 200
        while True:
            yield 0, 0

    monkeypatch.setattr(statblk, "get_read_write_rate_throughput_iter", fake_tpt)
    # Keep unit tests off the host's real sysfs / smartctl.
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", None)
    monkeypatch.setattr(statblk, "read_model_and_serial", lambda p: ("", ""))
    monkeypatch.setattr(statblk, "read_discard_support", lambda p: "N/A")
    monkeypatch.setattr(statblk, "read_size", lambda p: 1000)


def _patch_multicmd(monkeypatch, result):
    """Every run_command returns ``result``; records the commands it was given."""
    commands = []

    def run_command(cmd, *a, **k):
        commands.append(cmd)
        return result

    monkeypatch.setattr(statblk.multiCMD, "run_command", run_command)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    return commands


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


def test_filter_patterns(monkeypatch):
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


def test_invert_match_row_filter(monkeypatch):
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1", "/dev/nvme0n1"])
    mounts = _mount_table("/dev/sda1", "/")
    mounts["/dev/nvme0n1"] = [statblk.MountEntry("/mnt", "xfs", ["rw"])]
    monkeypatch.setattr(statblk, "parseMount", lambda: mounts)
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(
        output="NAME,MOUNTPOINT",
        filter_patterns=["nvme"],
        invert_match=True,
        timeout=2,
    )
    names = [r[0] for r in rows[1:]]
    assert "sda1" in names
    assert not any("nvme" in n for n in names)


def test_invert_match_devname_only(monkeypatch):
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
    # -D + invert: exclude devices whose name matches "nvme"; mountpoint
    # "/mnt/nvme-backup" must not keep sda1 out (devname-only path).
    rows = statblk.get_drives_info(
        output="NAME,MOUNTPOINT",
        filter_patterns=["nvme"],
        invert_match=True,
        match_devname_only=True,
        timeout=2,
    )
    assert [r[0] for r in rows[1:]] == ["sda1"]
    assert rows[1][1] == "/mnt/nvme-backup"


def test_invert_match_no_patterns_header_only(monkeypatch):
    _patch_linux_basics(monkeypatch)
    fake = FakeCmdResult([], 0)
    monkeypatch.setattr(statblk.multiCMD, "run_command", lambda *a, **k: fake)
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: None)
    monkeypatch.setattr(statblk.multiCMD, "format_bytes", lambda n, **k: str(n))
    rows = statblk.get_drives_info(
        output="NAME,MOUNTPOINT", invert_match=True, timeout=2
    )
    assert rows == [["NAME", "MOUNTPOINT"]]


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


def test_mounts_reread_between_get_drives_info_calls(tmp_path, monkeypatch):
    _patch_linux_basics(monkeypatch)
    monkeypatch.setattr(statblk, "parseMount", REAL_PARSE_MOUNT)
    mountinfo = tmp_path / "mountinfo"
    monkeypatch.setattr(statblk, "MOUNTINFO_PATH", str(mountinfo))
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    mountinfo.write_text("100 99 8:1 / /old rw - ext4 /dev/sda1 rw\n")
    r1 = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    mountinfo.write_text("100 99 8:1 / /new rw - ext4 /dev/sda1 rw\n")
    r2 = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    assert r1[1:] == [["sda1", "/old"]]
    assert r2[1:] == [["sda1", "/new"]]


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


def test_smart_join_bounded_by_timeout(tmp_path, monkeypatch):
    make_sysfs_block(tmp_path, "sda", size_sectors=1)
    _patch_linux_basics(monkeypatch)
    redirect_sys_class_block(tmp_path, monkeypatch)
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", "/usr/sbin/smartctl")
    smart = FakeCmdResult(
        ["SMART overall-health self-assessment test result: PASSED"], 0
    )
    _patch_multicmd(monkeypatch, smart)
    rows = statblk.get_drives_info(output="NAME,SMART", timeout=9)
    assert len(smart.join_timeouts) == 1
    assert 8 < smart.join_timeouts[0] <= 9
    assert rows[1][0] == "sda1"
    assert rows[1][1] == "OK"

def test_exclude_does_not_shrink_later_default_output(monkeypatch):
    _patch_linux_basics(monkeypatch)
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    statblk.get_drives_info(exclude="SMART,READ,WRITE", timeout=2)
    rows = statblk.get_drives_info(timeout=2)
    assert rows[0] == [
        "NAME", "FSTYPE", "SIZE", "FSUSE%", "MOUNTPOINT", "SMART", "LABEL",
        "UUID", "MODEL", "SERIAL", "DISCARD", "READ", "WRITE",
    ]


def test_model_serial_come_from_lsblk_parent_disk(monkeypatch):
    _patch_linux_basics(monkeypatch, devices=["/dev/sda", "/dev/sda1"], mounts=defaultdict(list))
    # sysfs only exposes the 16-byte SCSI INQUIRY model and the WWN
    monkeypatch.setattr(
        statblk, "read_model_and_serial", lambda p: ("WDC WUH721414AL", "naa.5000cca29bf57c9d")
    )
    commands = _patch_multicmd(monkeypatch, FakeCmdResult([
        'NAME="/dev/sda" SIZE="1000" FSTYPE="" UUID="" LABEL="" MODEL="WDC WUH721414ALE604" SERIAL="QGKTNKHT"',
        'NAME="/dev/sda1" SIZE="500" FSTYPE="xfs" UUID="" LABEL="" MODEL="" SERIAL=""',
    ]))
    rows = statblk.get_drives_info(output="NAME,MODEL,SERIAL", timeout=2)
    assert rows[1:] == [
        ["sda", "WDC WUH721414ALE604", "QGKTNKHT"],
        ["sda1", "WDC WUH721414ALE604", "QGKTNKHT"],
    ]
    assert any(c.startswith("lsblk ") for c in commands)


def test_model_serial_fall_back_to_sysfs_when_lsblk_fails(monkeypatch):
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1"], mounts=defaultdict(list))
    monkeypatch.setattr(statblk, "read_model_and_serial", lambda p: ("SysfsModel", "SysfsSerial"))
    _patch_multicmd(monkeypatch, FakeCmdResult([], returncode=1))
    rows = statblk.get_drives_info(output="NAME,MODEL,SERIAL", timeout=2)
    assert rows[1:] == [["sda1", "SysfsModel", "SysfsSerial"]]


def test_missing_smartctl_hint_only_in_debug(monkeypatch, capsys):
    _patch_linux_basics(monkeypatch)
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    monkeypatch.setattr(statblk, "_DEBUG_MODE", False)
    statblk.get_drives_info(output="NAME,SMART", timeout=2)
    assert "smartctl" not in capsys.readouterr().err
    statblk.get_drives_info(output="NAME,SMART", timeout=2, debug=True)
    assert "smartctl" in capsys.readouterr().err


def test_smartctl_only_runs_on_disks_with_sysfs_device(tmp_path, monkeypatch):
    make_sysfs_block(tmp_path, "sda", size_sectors=1)  # physical: has device/
    make_sysfs_block(tmp_path, "loop0", size_sectors=1, with_device=False)
    make_sysfs_block(tmp_path, "dm-0", size_sectors=1, with_device=False)
    _patch_linux_basics(
        monkeypatch, devices=["/dev/sda1", "/dev/loop0", "/dev/dm-0"], mounts=defaultdict(list)
    )
    monkeypatch.setattr(
        statblk, "get_partition_parent_name", lambda p: {"/dev/sda1": "/dev/sda"}.get(p, p)
    )
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", "/usr/sbin/smartctl")
    redirect_sys_class_block(tmp_path, monkeypatch)
    commands = _patch_multicmd(monkeypatch, FakeCmdResult(
        ["SMART overall-health self-assessment test result: PASSED"]
    ))
    rows = statblk.get_drives_info(output="NAME,SMART", timeout=2)
    assert [c for c in commands if "smartctl" in c] == ["/usr/sbin/smartctl -H /dev/sda"]
    assert rows[1:] == [["dm-0", ""], ["loop0", ""], ["sda1", "OK"]]


def test_sysfs_caches_refresh_between_calls(tmp_path, monkeypatch):
    # Watch mode: a drive swapped into the same bay keeps the same sysfs path.
    block = make_sysfs_block(tmp_path, "sda", size_sectors=1, discard_max_bytes=0)
    _patch_linux_basics(monkeypatch, devices=["/dev/sda"], mounts=defaultdict(list))
    monkeypatch.setattr(statblk, "read_discard_support", REAL_READ_DISCARD_SUPPORT)
    redirect_sys_class_block(tmp_path, monkeypatch)
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    first = statblk.get_drives_info(output="NAME,DISCARD", timeout=2)
    (block / "queue" / "discard_max_bytes").write_text("4096")
    second = statblk.get_drives_info(output="NAME,DISCARD", timeout=2)
    assert first[1:] == [["sda", "No"]]
    assert second[1:] == [["sda", "Yes"]]


def test_stuck_smartctl_waited_once_and_marked_timeout(tmp_path, monkeypatch):
    # smartctl in D-state on a dying disk: terminate/kill can't reap it.
    make_sysfs_block(tmp_path, "sda", size_sectors=1)
    _patch_linux_basics(
        monkeypatch, devices=["/dev/sda1", "/dev/sda2", "/dev/sda3"], mounts=defaultdict(list)
    )
    redirect_sys_class_block(tmp_path, monkeypatch)
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", "/usr/sbin/smartctl")
    stuck = FakeCmdResult([], None, alive=True)
    _patch_multicmd(monkeypatch, stuck)
    join_threads_calls = []
    monkeypatch.setattr(statblk.multiCMD, "join_threads", lambda **k: join_threads_calls.append(k))
    rows = statblk.get_drives_info(output="NAME,SMART", timeout=2)
    assert rows[1:] == [["sda1", "TIMEOUT"], ["sda2", "TIMEOUT"], ["sda3", "TIMEOUT"]]
    assert len(stuck.join_timeouts) == 1
    assert len(join_threads_calls) == 1


def test_hung_mount_shown_as_timeout(monkeypatch):
    mounts = _mount_table("/dev/sda1", "/mnt/nfs-gone")
    _patch_linux_basics(monkeypatch, mounts=mounts)
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, timeout=None: None)
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    rows = statblk.get_drives_info(output="NAME,SIZE,FSUSE%,MOUNTPOINT", timeout=2)
    assert rows[1:] == [["sda1", "", "TIMEOUT", "/mnt/nfs-gone"]]


def test_autofs_mounts_ignored(tmp_path, monkeypatch):
    # stat-ing an autofs mountpoint triggers the automount (df skips them too)
    mountinfo = tmp_path / "mountinfo"
    mountinfo.write_text(
        "40 30 0:40 / /proc/sys/fs/binfmt_misc rw,relatime - autofs systemd-1 rw,fd=33\n"
        "100 99 8:1 / /data rw - ext4 /dev/sda1 rw\n"
    )
    monkeypatch.setattr(statblk, "MOUNTINFO_PATH", str(mountinfo))
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    table = REAL_PARSE_MOUNT()
    assert list(table) == ["/dev/sda1"]


def test_unmounted_size_from_lsblk_skips_sysfs_read(monkeypatch):
    _patch_linux_basics(monkeypatch, mounts=defaultdict(list))
    reads = []
    monkeypatch.setattr(statblk, "read_size", lambda p: reads.append(p) or 1)
    _patch_multicmd(monkeypatch, FakeCmdResult(
        ['NAME="/dev/sda1" SIZE="1000" FSTYPE="" UUID="" LABEL="" MODEL="" SERIAL=""']
    ))
    rows = statblk.get_drives_info(output="NAME,SIZE", timeout=2)
    assert rows[1:] == [["sda1", "1000B"]]
    assert reads == []


def test_invert_match_no_patterns_devname_only_header_only(monkeypatch):
    _patch_linux_basics(monkeypatch)
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    rows = statblk.get_drives_info(
        output="NAME,MOUNTPOINT", invert_match=True, match_devname_only=True, timeout=2
    )
    assert rows == [["NAME", "MOUNTPOINT"]]


def test_devices_in_natural_order(monkeypatch):
    devices = ["/dev/sda10", "/dev/sda2", "/dev/sda1", "/dev/nvme0n1p10", "/dev/nvme0n1p2", "/dev/sda"]
    _patch_linux_basics(monkeypatch, devices=devices, mounts=defaultdict(list))
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    rows = statblk.get_drives_info(output="NAME", timeout=2)
    assert [r[0] for r in rows[1:]] == [
        "nvme0n1p2", "nvme0n1p10", "sda", "sda1", "sda2", "sda10",
    ]


def _make_dm_device(tmp_path, kname, dm_name):
    block = make_sysfs_block(tmp_path, kname, size_sectors=1, with_device=False)
    (block / "dm").mkdir()
    (block / "dm" / "name").write_text(dm_name + "\n")
    return block


def test_dm_devices_shown_by_mapper_name(tmp_path, monkeypatch):
    _make_dm_device(tmp_path, "dm-1", "pve-root")
    make_sysfs_block(tmp_path, "sda1", size_sectors=1)
    _patch_linux_basics(monkeypatch, devices=["/dev/dm-1", "/dev/sda1"], mounts=defaultdict(list))
    redirect_sys_class_block(tmp_path, monkeypatch)
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    short = statblk.get_drives_info(output="NAME", timeout=2)
    full = statblk.get_drives_info(output="NAME", full=True, timeout=2)
    assert [r[0] for r in short[1:]] == ["pve-root", "sda1"]
    assert [r[0] for r in full[1:]] == ["/dev/mapper/pve-root", "/dev/sda1"]


def test_devname_filter_matches_mapper_name(tmp_path, monkeypatch):
    _make_dm_device(tmp_path, "dm-1", "pve-root")
    _make_dm_device(tmp_path, "dm-0", "pve-swap")
    _patch_linux_basics(monkeypatch, devices=["/dev/dm-0", "/dev/dm-1"], mounts=defaultdict(list))
    redirect_sys_class_block(tmp_path, monkeypatch)
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    rows = statblk.get_drives_info(
        output="NAME", filter_patterns=["root"], match_devname_only=True, timeout=2
    )
    assert [r[0] for r in rows[1:]] == ["pve-root"]


def _squashfs_mounts():
    return defaultdict(
        list,
        {
            "/dev/loop0": [statblk.MountEntry("/snap/core22/2437", "squashfs", ["ro"])],
            "/dev/loop1": [statblk.MountEntry("/mnt/image", "ext4", ["rw"])],
            "/dev/sdb1": [statblk.MountEntry("/mnt/live", "squashfs", ["ro"])],
        },
    )


def test_squashfs_loop_mounts_hidden_by_default(monkeypatch):
    devices = ["/dev/loop0", "/dev/loop1", "/dev/sdb1"]
    _patch_linux_basics(monkeypatch, devices=devices, mounts=_squashfs_mounts())
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    hidden = statblk.get_drives_info(output="NAME,FSTYPE", timeout=2)
    # Only the snap loop goes: a loop disk image and a non-loop squashfs stay.
    assert hidden[1:] == [["loop1", "ext4"], ["sdb1", "squashfs"]]
    shown = statblk.get_drives_info(output="NAME,FSTYPE", show_squashfs=True, timeout=2)
    assert [r[0] for r in shown[1:]] == ["loop0", "loop1", "sdb1"]


def test_squashfs_loop_hidden_regardless_of_output_columns(monkeypatch):
    # Mounted FSTYPE comes from mountinfo, so hiding works without the FSTYPE column.
    _patch_linux_basics(monkeypatch, devices=["/dev/loop0"], mounts=_squashfs_mounts())
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    rows = statblk.get_drives_info(output="NAME,MOUNTPOINT", timeout=2)
    assert rows[1:] == []


def test_unmounted_squashfs_loop_hidden_by_lsblk_fstype(monkeypatch):
    _patch_linux_basics(monkeypatch, devices=["/dev/loop0", "/dev/loop1"], mounts=defaultdict(list))
    _patch_multicmd(monkeypatch, FakeCmdResult([
        'NAME="/dev/loop0" SIZE="1000" FSTYPE="squashfs" UUID="" LABEL=""',
        'NAME="/dev/loop1" SIZE="1000" FSTYPE="ext4" UUID="" LABEL=""',
    ], 0))
    rows = statblk.get_drives_info(output="NAME,FSTYPE", timeout=2)
    assert rows[1:] == [["loop1", "ext4"]]
    shown = statblk.get_drives_info(output="NAME,FSTYPE", show_squashfs=True, timeout=2)
    assert [r[0] for r in shown[1:]] == ["loop0", "loop1"]


_FORMATTED_AND_BLANK_LSBLK = [
    'NAME="/dev/sda1" SIZE="1000" FSTYPE="ext4" UUID="u" LABEL="L"',
    'NAME="/dev/sda2" SIZE="2000" FSTYPE="" UUID="" LABEL=""',
]


def test_formated_only_without_fstype_column(monkeypatch):
    # -F needs FSTYPE even when it isn't a displayed column.
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1", "/dev/sda2"], mounts=defaultdict(list))
    _patch_multicmd(monkeypatch, FakeCmdResult(_FORMATTED_AND_BLANK_LSBLK, 0))
    rows = statblk.get_drives_info(output="NAME,SIZE", formated_only=True, timeout=2)
    assert rows == [["NAME", "SIZE"], ["sda1", "1000B"]]


def test_formated_only_runs_lsblk_without_lsblk_columns(monkeypatch):
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1", "/dev/sda2"], mounts=defaultdict(list))
    commands = _patch_multicmd(monkeypatch, FakeCmdResult(_FORMATTED_AND_BLANK_LSBLK, 0))
    rows = statblk.get_drives_info(output="NAME,MOUNTPOINT", formated_only=True, timeout=2)
    assert any(cmd.startswith("lsblk") for cmd in commands)
    assert rows == [["NAME", "MOUNTPOINT"], ["sda1", ""]]


def _hardware_and_virtual(tmp_path, monkeypatch):
    make_sysfs_block(tmp_path, "sda", size_sectors=1)  # physical: has device/
    make_sysfs_block(tmp_path, "loop0", size_sectors=1, with_device=False)
    _patch_linux_basics(monkeypatch, devices=["/dev/sda1", "/dev/loop0"], mounts=defaultdict(list))
    monkeypatch.setattr(
        statblk, "get_partition_parent_name", lambda p: {"/dev/sda1": "/dev/sda"}.get(p, p)
    )
    redirect_sys_class_block(tmp_path, monkeypatch)


def test_missing_smartctl_marks_hardware_disks(tmp_path, monkeypatch):
    _hardware_and_virtual(tmp_path, monkeypatch)
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", None)
    _patch_multicmd(monkeypatch, FakeCmdResult([], 0))
    rows = statblk.get_drives_info(output="NAME,SMART", timeout=2)
    assert rows[1:] == [["loop0", ""], ["sda1", "NO SMARTCTL"]]


def test_smart_without_verdict_is_unknown(tmp_path, monkeypatch):
    _hardware_and_virtual(tmp_path, monkeypatch)
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", "/usr/sbin/smartctl")
    _patch_multicmd(monkeypatch, FakeCmdResult(
        ["/dev/sda: DELL or MegaRaid controller, please try adding '-d megaraid,N'"]
    ))
    rows = statblk.get_drives_info(output="NAME,SMART", timeout=2)
    assert rows[1:] == [["loop0", ""], ["sda1", "UNKNOWN"]]
