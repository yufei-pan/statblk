"""--check through the real main() and get_drives_info(), with only the commands faked (multiCMD.run_command) and
the host's devices described: on macOS the test Mac's own /dev, mount and diskutil output (tests/macos26.txt).
Each case forces one outcome: what a stopped command, a filter or a size read as 0 does to the exit and the rows."""
import pytest

import statblk
from fakes import MACOS26_DEV, MACOS26_DISKUTIL, MACOS26_MOUNT, FakeCmdResult

CUT = 124  # multiCMD's return code for a command --timeout stopped


def _cut_line(command, timeout):
    return statblk.cut_note(command, timeout) + "\n"


def _run(monkeypatch, capsys, argv, run_command):
    """main() with `argv`; return (exit, names of the rows printed, stdout, stderr)."""
    tables = []
    monkeypatch.setattr(statblk.multiCMD, "run_command", run_command)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda rows, **k: tables.append(rows) or "T")
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", "/usr/sbin/smartctl")
    monkeypatch.setattr(statblk, "find_stuck_smartctl", lambda older_than: set())
    monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: (1000, 350, 650))  # 35% used
    monkeypatch.setattr(statblk.sys, "argv", ["statblk"] + argv)
    code = statblk.main()
    out, err = capsys.readouterr()
    names = [row[0] for table in tables for row in table[1:]]
    return code or 0, names, out, err


def _smartctl(command, failing):
    verdict = "FAILED!" if command.endswith(" " + failing) else "PASSED"
    return FakeCmdResult(["SMART overall-health self-assessment test result: " + verdict])


# macOS: the test Mac. disk0 is the physical SSD, with no filesystem and nothing mounted; disk3 is the APFS container
# whose volumes are mounted at / and /System/Volumes/*.

MAC_NAMES = [d[len("/dev/"):] for d in MACOS26_DEV]
DISK0 = [n for n in MAC_NAMES if n.startswith("disk0")]
DISK3 = [n for n in MAC_NAMES if n.startswith("disk3")]
DISK1_STARTS = MACOS26_DISKUTIL.index("   Device Node:               /dev/disk1")
DISK0_SIZE_LINE = MACOS26_DISKUTIL.index("   Disk Size:                 500.3 GB (500277792768 Bytes) "
                                         "(exactly 977105064 512-Byte-Units)")
DISKUTIL_STOPS = {  # diskutil stopped: before its first line, inside disk0 before its size, after its last line
    "before its first line": [],
    "in the middle of a device": MACOS26_DISKUTIL[:DISK0_SIZE_LINE],
    "after the last device": MACOS26_DISKUTIL,
}


def _mac(monkeypatch, failing, diskutil=(MACOS26_DISKUTIL, 0), mount=(MACOS26_MOUNT, 0)):
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")
    monkeypatch.setattr(statblk, "get_blocks", lambda: list(MACOS26_DEV))
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p in MACOS26_DEV)

    def run_command(command, *a, **k):
        if "smartctl" in command:
            return _smartctl(command, failing)
        if command == "mount":
            return FakeCmdResult(*mount)
        assert "diskutil" in command, command
        return FakeCmdResult(*diskutil)
    return run_command


def test_mac_unmounted_failing_disk_with_no_diskutil_column(monkeypatch, capsys):
    # No column needs diskutil, so it does not run and no size is read: disk0's rows stay, and its SMART is judged.
    run = _mac(monkeypatch, "/dev/disk0")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "-o", "NAME,FSUSE%,SMART"], run) == (1, DISK0, "T\n", "")


@pytest.mark.parametrize("stop", DISKUTIL_STOPS)
def test_mac_diskutil_stopped_still_shows_the_unmounted_failing_disk(monkeypatch, capsys, stop):
    run = _mac(monkeypatch, "/dev/disk0", diskutil=(DISKUTIL_STOPS[stop], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (1, DISK0, "T\n", _cut_line("diskutil", 2))


@pytest.mark.parametrize("stop", DISKUTIL_STOPS)
def test_mac_diskutil_stopped_on_a_healthy_mac_is_healthy_and_silent(monkeypatch, capsys, stop):
    # What a stopped diskutil leaves out (SIZE, FSTYPE, LABEL...) is shown, not checked.
    run = _mac(monkeypatch, "/dev/none", diskutil=(DISKUTIL_STOPS[stop], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (0, [], "", "")


def test_mac_healthy_is_silent(monkeypatch, capsys):
    run = _mac(monkeypatch, "/dev/none")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (0, [], "", "")


@pytest.mark.parametrize("argv, expected", [
    ([], 3),  # the filesystems it did not list have no FSUSE%
    (["-x", "FSUSE%"], 0),  # SMART only: every disk is still listed
    (["-M", "-x", "FSUSE%"], 3),  # -M: which disks are mounted is not known
])
def test_mac_mount_stopped_on_a_healthy_mac(monkeypatch, capsys, argv, expected):
    run = _mac(monkeypatch, "/dev/none", mount=([], CUT))
    err = _cut_line("mount", 2) if expected else ""
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run) == (expected, [], "", err)


@pytest.mark.parametrize("argv", [["-x", "FSUSE%"], ["-F", "-x", "FSUSE%"], ["-o", "NAME,SMART", "-x", "FSUSE%"]])
def test_mac_mount_stopped_still_shows_the_mounted_failing_disk(monkeypatch, capsys, argv):
    # disk3's volumes, not listed by the stopped mount, stay as unmounted rows with their SMART.
    run = _mac(monkeypatch, "/dev/disk3", mount=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run) == (1, DISK3, "T\n", _cut_line("mount", 2))


def test_mac_diskutil_stopped_with_a_pattern_is_unknown(monkeypatch, capsys):
    # A pattern (not -D) can match a cell diskutil fills, so the rows it keeps are not known.
    run = _mac(monkeypatch, "/dev/none", diskutil=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "disk3"], run) == (3, [], "", _cut_line("diskutil", 2))


def _zero_size(lines, devices):
    """diskutil's lines with a size of 0 Bytes for each of `devices`."""
    zeroed, device = [], None
    for line in lines:
        if line.split(":", 1)[0].strip() == "Device Node":
            device = line.split(":", 1)[1].strip()
        if device in devices and line.split(":", 1)[0].strip() == "Disk Size":
            line = "   Disk Size:                 0 B (0 Bytes) (exactly 0 512-Byte-Units)"
        zeroed.append(line)
    return zeroed


@pytest.mark.parametrize("argv, expected", [([], (0, [], "", "")), (["--show_zero_size_devices"], (1, DISK0, "T\n", ""))])
def test_mac_disk_whose_size_reads_zero_is_checked_only_when_shown(monkeypatch, capsys, argv, expected):
    # A size diskutil read as 0 still hides the device (the zero-size question waits on the user).
    zeroed = _zero_size(MACOS26_DISKUTIL, ["/dev/" + n for n in DISK0])
    run = _mac(monkeypatch, "/dev/disk0", diskutil=(zeroed, 0))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run) == expected


def test_mac_active_only_keeps_the_rows(monkeypatch, capsys):
    # macOS has no throughput to read, so -A drops nothing there.
    run = _mac(monkeypatch, "/dev/disk3")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "-A"], run) == (1, DISK3, "T\n", "")


# Linux: sda1 is mounted at /; sdb fails its SMART, and its filesystem sdb1 is not mounted.

LSBLK = [
    'NAME="/dev/sda" SIZE="1073741824" FSTYPE="" UUID="" LABEL="" MODEL="M" SERIAL="S1"',
    'NAME="/dev/sda1" SIZE="1073741824" FSTYPE="ext4" UUID="u1" LABEL="" MODEL="" SERIAL=""',
    'NAME="/dev/sdb" SIZE="1073741824" FSTYPE="" UUID="" LABEL="" MODEL="M" SERIAL="S2"',
    'NAME="/dev/sdb1" SIZE="1073741824" FSTYPE="ext4" UUID="u2" LABEL="" MODEL="" SERIAL=""',
]
LSBLK_STOPPED = {"stopped": ([], CUT), "still running": ([], None, True)}


def _linux(monkeypatch, tmp_path, failing, lsblk=(LSBLK, 0), zero=()):
    mountinfo = tmp_path / "mountinfo"
    mountinfo.write_text("100 99 8:1 / / rw,relatime - ext4 /dev/sda1 rw\n")
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    monkeypatch.setattr(statblk, "MOUNTINFO_PATH", str(mountinfo))
    monkeypatch.setattr(statblk, "get_blocks", lambda: ["/dev/sda", "/dev/sda1", "/dev/sdb", "/dev/sdb1"])
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_partition_parent_name", lambda p: p.rstrip("0123456789") if p else None)
    monkeypatch.setattr(statblk, "has_sysfs_device", lambda disk: True)
    monkeypatch.setattr(statblk, "read_size", lambda p: 0 if p.rsplit("/", 1)[-1] in zero else 1 << 30)
    monkeypatch.setattr(statblk, "read_model_and_serial", lambda p: ("", ""))
    monkeypatch.setattr(statblk, "read_discard_support", lambda p: "N/A")
    monkeypatch.setattr(statblk, "build_symlink_dict", lambda d: {})
    monkeypatch.setattr(statblk, "get_read_write_rate_throughput_iter", lambda p: iter(lambda: (0, 0), None))
    monkeypatch.setattr(statblk.shutil, "which", lambda name, *a, **k: None if lsblk[1] == 127 else "/usr/bin/" + name)

    def run_command(command, *a, **k):
        if "smartctl" in command:
            return _smartctl(command, failing)
        assert command.startswith("lsblk"), command
        return FakeCmdResult(*lsblk)
    return run_command


@pytest.mark.parametrize("stop", LSBLK_STOPPED)
def test_linux_formated_only_lsblk_stopped_still_shows_the_failing_disk(monkeypatch, capsys, tmp_path, stop):
    # sdb1's FSTYPE comes only from lsblk: not read, so -F keeps sdb and sdb1, and sdb's SMART is judged.
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=LSBLK_STOPPED[stop])
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "-F"], run) == (
        1, ["sdb", "sdb1"], "T\n", _cut_line("lsblk", 0.5))


def test_linux_formated_only_without_lsblk_still_shows_the_failing_disk(monkeypatch, capsys, tmp_path):
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=([], 127))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "-F"], run) == (
        1, ["sdb", "sdb1"], "T\n", statblk.LSBLK_MISSING_NOTE + "\n")


@pytest.mark.parametrize("stop", LSBLK_STOPPED)
def test_linux_formated_only_lsblk_stopped_on_a_healthy_host_is_healthy_and_silent(monkeypatch, capsys, tmp_path, stop):
    run = _linux(monkeypatch, tmp_path, "/dev/none", lsblk=LSBLK_STOPPED[stop])
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "-F"], run) == (0, [], "", "")


def test_linux_formated_only_lsblk_answered_drops_the_unformatted_rows(monkeypatch, capsys, tmp_path):
    # The control: lsblk answered, so sda and sdb (no filesystem) go, and sdb1 carries sdb's SMART.
    run = _linux(monkeypatch, tmp_path, "/dev/sdb")
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "-F"], run) == (1, ["sdb1"], "T\n", "")


@pytest.mark.parametrize("argv, expected", [
    (["sda"], (3, [], "", _cut_line("lsblk", 0.5))),  # a pattern can match a cell lsblk fills
    (["-D", "sda"], (0, [], "", "")),  # -D matches device names, which lsblk does not give
])
def test_linux_lsblk_stopped_with_a_pattern(monkeypatch, capsys, tmp_path, argv, expected):
    run = _linux(monkeypatch, tmp_path, "/dev/none", lsblk=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5"] + argv, run) == expected


@pytest.mark.parametrize("argv, expected", [([], (0, [], "", "")), (["--show_zero_size_devices"], (1, ["sdb", "sdb1"], "T\n", ""))])
def test_linux_disk_whose_size_reads_zero_is_checked_only_when_shown(monkeypatch, capsys, tmp_path, argv, expected):
    lsblk = [line.replace('SIZE="1073741824"', 'SIZE="0"') if "sdb" in line else line for line in LSBLK]
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=(lsblk, 0), zero=("sdb", "sdb1"))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5"] + argv, run) == expected
