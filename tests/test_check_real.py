"""--check through the real main() and get_drives_info(), with only the commands faked (multiCMD.run_command) and
the host's devices described: on macOS the test Mac's own /dev, mount and diskutil output (tests/macos26.txt).
Each case forces one outcome: what a stopped command, a failed statvfs, a filter or a size read as 0 does to the
exit and the rows."""
import errno

import pytest

import statblk
from fakes import MACOS26_DEV, MACOS26_DISKUTIL, MACOS26_MOUNT, FakeCmdResult

CUT = 124  # multiCMD's return code for a command --timeout stopped
NOT_FOUND = 127  # and for one it did not find
FAILED = 1
DID_NOT_ANSWER = pytest.mark.parametrize("returncode", [CUT, NOT_FOUND, FAILED], ids=["stopped", "not found", "failed"])
EIO = OSError(errno.EIO, "Input/output error")  # statvfs of a failing disk's mount, a dead FUSE or NFS mount
DENIED = PermissionError(errno.EACCES, "Permission denied")  # statvfs under a directory the user cannot search
STATVFS_ERRORS = pytest.mark.parametrize("error", [EIO, DENIED], ids=["EIO", "PermissionError"])


def _cut_line(command, timeout, returncode=CUT):
    return statblk.cut_note(command, timeout, returncode) + "\n"


def _run_tables(monkeypatch, capsys, argv, run_command, usage=(1000, 350, 650)):
    """main() with `argv`; return (exit, the tables printed, stdout, stderr). usage is what each mount's statvfs
    answers (total, used, avail: 35% used), or an exception that the real get_statvfs_use_size meets."""
    tables = []
    monkeypatch.setattr(statblk.multiCMD, "run_command", run_command)
    monkeypatch.setattr(statblk.multiCMD, "set_sudo", lambda x: None)
    monkeypatch.setattr(statblk.multiCMD, "pretty_format_table", lambda rows, **k: tables.append(rows) or "T")
    monkeypatch.setattr(statblk, "SMARTCTL_PATH", "/usr/sbin/smartctl")
    monkeypatch.setattr(statblk, "find_stuck_smartctl", lambda older_than: set())
    if isinstance(usage, Exception):
        def failing(path):
            raise usage

        monkeypatch.setattr(statblk.os, "statvfs", failing)
    else:
        monkeypatch.setattr(statblk, "get_statvfs_use_size", lambda mp, *a, **k: usage)
    monkeypatch.setattr(statblk.sys, "argv", ["statblk"] + argv)
    code = statblk.main()
    out, err = capsys.readouterr()
    return code or 0, tables, out, err


def _run(monkeypatch, capsys, argv, run_command, usage=(1000, 350, 650)):
    """_run_tables with the tables reduced to the names of the rows printed: (exit, names, stdout, stderr)."""
    code, tables, out, err = _run_tables(monkeypatch, capsys, argv, run_command, usage)
    return code, [row[0] for table in tables for row in table[1:]], out, err


def _smartctl(command, failing, unreadable=None):
    # Every device not named answers PASSED. disk1 to disk3 of the capture are virtual (APFS containers): whether
    # smartctl on a real Mac answers for them is not verified (the test Mac has no smartctl); an UNKNOWN there would
    # make a real --check exit 3 where these tests say 0.
    if unreadable and command.endswith(" " + unreadable):
        return FakeCmdResult(["Unable to detect device type"])  # no verdict: SMART UNKNOWN
    verdict = "FAILED!" if command.endswith(" " + failing) else "PASSED"
    return FakeCmdResult(["SMART overall-health self-assessment test result: " + verdict])


# macOS: the test Mac. disk0 is the physical SSD, with no filesystem and nothing mounted; disk3 is the APFS container
# whose volumes are mounted at / and /System/Volumes/* (disk3s1 and disk3s3 are not mounted).

MAC_NAMES = [d[len("/dev/"):] for d in MACOS26_DEV]
DISK0 = [n for n in MAC_NAMES if n.startswith("disk0")]
DISK3 = [n for n in MAC_NAMES if n.startswith("disk3")]
MOUNTED = ["disk1s1", "disk1s2", "disk1s3", "disk3s1s1", "disk3s2", "disk3s4", "disk3s5", "disk3s6"]  # block devices
DISK0_SIZE_LINE = MACOS26_DISKUTIL.index("   Disk Size:                 500.3 GB (500277792768 Bytes) "
                                         "(exactly 977105064 512-Byte-Units)")
DISKUTIL_STOPS = {  # diskutil stopped: before its first line, inside disk0 before its size, after its last line
    "before its first line": [],
    "in the middle of a device": MACOS26_DISKUTIL[:DISK0_SIZE_LINE],
    "after the last device": MACOS26_DISKUTIL,
}


def _mac(monkeypatch, failing, diskutil=(MACOS26_DISKUTIL, 0), mount=(MACOS26_MOUNT, 0), dev=MACOS26_DEV,
         unreadable=None):
    """The Mac's commands: diskutil and mount as (lines, return code); smartctl fails `failing` and gives no verdict
    for `unreadable`. The function's .given lists the commands it was given."""
    monkeypatch.setattr(statblk, "IS_DARWIN", True)
    monkeypatch.setattr(statblk, "DISKUTIL_PATH", "/usr/sbin/diskutil")
    monkeypatch.setattr(statblk, "MOUNT_PATH", "/sbin/mount")
    monkeypatch.setattr(statblk, "get_blocks", lambda: list(dev))
    monkeypatch.setattr(statblk, "is_block_device", lambda p: p in dev)
    given = []

    def run_command(command, *a, **k):
        given.append(command)
        if "smartctl" in command:
            return _smartctl(command, failing, unreadable)
        if command == "/sbin/mount":
            return FakeCmdResult(*mount)
        assert "diskutil" in command, command
        return FakeCmdResult(*diskutil)
    run_command.given = given
    return run_command


def test_mac_unmounted_failing_disk_is_judged_from_the_real_capture(monkeypatch, capsys):
    # The SSD itself (disk0): no filesystem, nothing mounted, so 1.62 never saw it.
    run = _mac(monkeypatch, "/dev/disk0")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (1, DISK0, "T\n", "")


def test_mac_unmounted_failing_disk_with_no_diskutil_column(monkeypatch, capsys):
    # No column needs diskutil, so it does not run and no size is read: disk0's rows stay, and its SMART is judged.
    run = _mac(monkeypatch, "/dev/disk0")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "-o", "NAME,FSUSE%,SMART"], run) == (1, DISK0, "T\n", "")
    assert not [command for command in run.given if "diskutil" in command]


@pytest.mark.parametrize("stop", DISKUTIL_STOPS)
def test_mac_diskutil_stopped_still_shows_the_unmounted_failing_disk(monkeypatch, capsys, stop):
    run = _mac(monkeypatch, "/dev/disk0", diskutil=(DISKUTIL_STOPS[stop], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (1, DISK0, "T\n", _cut_line("diskutil", 2))


@pytest.mark.parametrize("stop", DISKUTIL_STOPS)
def test_mac_diskutil_stopped_on_a_healthy_mac_is_healthy_and_silent(monkeypatch, capsys, stop):
    # What a stopped diskutil leaves out (SIZE, FSTYPE, LABEL...) is not checked, so nothing is printed.
    run = _mac(monkeypatch, "/dev/none", diskutil=(DISKUTIL_STOPS[stop], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (0, [], "", "")


def test_mac_healthy_is_silent(monkeypatch, capsys):
    run = _mac(monkeypatch, "/dev/none")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (0, [], "", "")


@pytest.mark.parametrize("argv, expected", [
    ([], 3),  # the filesystems it did not list have no FSUSE%
    (["-x", "FSUSE%"], 0),  # SMART only: every disk is still listed, and none is checked less
    (["-M", "-x", "FSUSE%"], 3),  # -M: which disks are mounted is not known
], ids=["plain", "SMART only", "-M"])
def test_mac_mount_stopped_on_a_healthy_mac(monkeypatch, capsys, argv, expected):
    run = _mac(monkeypatch, "/dev/none", mount=([], CUT))
    err = _cut_line("mount", 2) if expected else ""
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run) == (expected, [], "", err)


@pytest.mark.parametrize("argv", [[], ["-x", "FSUSE%"], ["-F", "-x", "FSUSE%"], ["-o", "NAME,SMART", "-x", "FSUSE%"]],
                         ids=["plain", "SMART only", "-F", "-o NAME,SMART"])
def test_mac_mount_stopped_still_shows_the_failing_disk_of_the_volumes_it_did_not_list(monkeypatch, capsys, argv):
    # The stopped mount lists no volume of disk3, so its mounted volumes come as unmounted rows with its SMART.
    run = _mac(monkeypatch, "/dev/disk3", mount=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run) == (1, DISK3, "T\n", _cut_line("mount", 2))


def test_mac_mount_stopped_hides_a_full_filesystem_as_unknown_not_healthy(monkeypatch, capsys):
    # Every mounted volume is 95% full. With the mount list that is a problem (1); a mount stopped before it
    # listed them cannot say, and 3 is the answer, not 0.
    full = (1000, 950, 50)
    run = _mac(monkeypatch, "/dev/none")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run, usage=full) == (1, MOUNTED, "T\n", "")
    run = _mac(monkeypatch, "/dev/none", mount=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run, usage=full) == (3, [], "", _cut_line("mount", 2))


@DID_NOT_ANSWER
def test_mac_mount_that_did_not_answer_is_unknown_over_a_full_filesystem_or_a_failing_disk(monkeypatch, capsys,
                                                                                            returncode):
    # 1.63 counted only a mount the timeout stopped: one that failed or was not found (cron's PATH has no /sbin; see
    # find_command) left FSUSE% blank and exited 0 over a full filesystem, and with -M over a failing disk.
    full = (1000, 950, 50)
    run = _mac(monkeypatch, "/dev/none", mount=([], returncode))
    note = _cut_line("mount", 2, returncode)
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run, usage=full) == (3, [], "", note)
    run = _mac(monkeypatch, "/dev/disk3", mount=([], returncode))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "-M"], run) == (3, [], "", note)


@pytest.mark.parametrize("argv", [["disk3"], ["-v", "zzz"]], ids=["pattern", "inverted pattern"])
def test_mac_diskutil_stopped_with_a_pattern_and_a_failing_disk_is_a_problem(monkeypatch, capsys, argv):
    # A problem beats the unknown a pattern makes of a stopped diskutil, and the note says what was stopped.
    run = _mac(monkeypatch, "/dev/disk3", diskutil=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run) == (1, DISK3, "T\n", _cut_line("diskutil", 2))


def test_mac_diskutil_stopped_with_a_pattern_is_unknown(monkeypatch, capsys):
    # A pattern (not -D) can match a cell diskutil fills, so the rows it keeps are not known.
    run = _mac(monkeypatch, "/dev/none", diskutil=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "disk3"], run) == (3, [], "", _cut_line("diskutil", 2))


def test_mac_formated_only_does_not_judge_a_disk_with_no_filesystem(monkeypatch, capsys):
    # -F is the operator's filter ("formatted only"): the physical SSD has no filesystem type, so it is not checked.
    run = _mac(monkeypatch, "/dev/disk0")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "-F"], run) == (0, [], "", "")


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


@pytest.mark.parametrize("argv, expected", [([], (0, [], "", "")), (["--show_zero_size_devices"], (1, DISK0, "T\n", ""))],
                         ids=["hidden", "shown"])
def test_mac_disk_whose_size_reads_zero_is_checked_only_when_shown(monkeypatch, capsys, argv, expected):
    # A size diskutil read as 0 hides the device: a known limitation (docs/limitations.md).
    zeroed = _zero_size(MACOS26_DISKUTIL, ["/dev/" + n for n in DISK0])
    run = _mac(monkeypatch, "/dev/disk0", diskutil=(zeroed, 0))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run) == expected


def test_mac_zero_size_whole_disk_is_judged_through_its_partitions(monkeypatch, capsys):
    # Only disk0 reads 0: its partition rows are shown and carry its SMART, so the known limitation (a whole disk
    # of size 0 with no partition row to show) does not apply.
    zeroed = _zero_size(MACOS26_DISKUTIL, ["/dev/disk0"])
    run = _mac(monkeypatch, "/dev/disk0", diskutil=(zeroed, 0))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (1, DISK0[1:], "T\n", "")


# An empty slot (a card reader with no card) has no SMART to read. diskutil says "Disk Size: Not applicable (no
# media)", which reads as a size of 0, so it is hidden and a healthy Mac stays healthy.
EMPTY_SLOT = ["", "   Device Identifier:         disk9", "   Device Node:               /dev/disk9", "",
              "   Disk Size:                 Not applicable (no media)", "   Solid State:               No"]


def test_mac_empty_slot_does_not_make_a_healthy_mac_unknown(monkeypatch, capsys):
    run = _mac(monkeypatch, "/dev/none", diskutil=(MACOS26_DISKUTIL + EMPTY_SLOT, 0), dev=MACOS26_DEV + ["/dev/disk9"],
               unreadable="/dev/disk9")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"], run) == (0, [], "", "")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "--show_zero_size_devices"], run) == (
        3, ["disk9"], "T\n", "")  # shown, its SMART cannot be read


def test_mac_active_only_keeps_the_rows(monkeypatch, capsys):
    # macOS has no throughput to read, so -A drops nothing there.
    run = _mac(monkeypatch, "/dev/disk3")
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "-A"], run) == (1, DISK3, "T\n", "")


# diskutil that exits with an error without being stopped: its output may end in the middle of a device.
# disk4 and its partition disk4s1 (unmounted) are the last devices; the output ends after the partition's Device Node
# line, with no File System Personality. After exit 0 that is a partition with no filesystem; after an error exit the
# line may only have been cut off.
DISK4 = ["", "   Device Identifier:         disk4", "   Device Node:               /dev/disk4", "",
         "   Disk Size:                 1.0 TB (1000204886016 Bytes) (exactly 1953525168 512-Byte-Units)", "",
         "   Device Identifier:         disk4s1", "   Device Node:               /dev/disk4s1"]


@pytest.mark.parametrize("returncode, expected", [
    (0, (0, [], "", "")),
    (1, (1, ["disk4", "disk4s1"], "T\n", _cut_line("diskutil", 2, FAILED))),  # a run that is not healthy names it
], ids=["exit 0", "exit 1"])
def test_mac_formated_only_diskutil_exit_decides_whether_the_type_was_read(monkeypatch, capsys, returncode, expected):
    # Only a diskutil that exited 0 answered in full: then disk4s1's blank type was read (no filesystem), and -F drops
    # it with disk4; after an error exit it was not read, so both stay and disk4's SMART is judged.
    run = _mac(monkeypatch, "/dev/disk4", diskutil=(MACOS26_DISKUTIL + DISK4, returncode),
               dev=MACOS26_DEV + ["/dev/disk4", "/dev/disk4s1"])
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "-F"], run) == expected


@pytest.mark.parametrize("stop", DISKUTIL_STOPS)
def test_mac_formated_only_with_a_stopped_diskutil_still_shows_the_unformatted_failing_disk(monkeypatch, capsys, stop):
    # diskutil did not answer in full, so disk0's blank type was not read: -F keeps it and its SMART is judged.
    run = _mac(monkeypatch, "/dev/disk0", diskutil=(DISKUTIL_STOPS[stop], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "2", "-F"], run) == (1, DISK0, "T\n", _cut_line("diskutil", 2))


# statvfs fails on the mounted volumes (a dead disk's EIO, a mount the user cannot search): the row stays with no
# size and FSUSE% ERROR, which --check counts as unknown, and the disk's SMART is still judged through the row.

@STATVFS_ERRORS
@pytest.mark.parametrize("timeout", ["0", "2"], ids=["no limit", "in a thread"])
def test_mac_statvfs_error_is_unknown_not_healthy(monkeypatch, capsys, error, timeout):
    run = _mac(monkeypatch, "/dev/none")
    code, tables, out, err = _run_tables(monkeypatch, capsys, ["--check", "-t", timeout], run, usage=error)
    assert (code, out, err) == (3, "T\n", "")
    assert [row[0] for row in tables[0][1:]] == MOUNTED
    assert {row[tables[0][0].index("FSUSE%")] for row in tables[0][1:]} == {"ERROR"}


@STATVFS_ERRORS
@pytest.mark.parametrize("argv", [[], ["-M"], ["-F"]], ids=["plain", "-M", "-F"])
def test_mac_statvfs_error_still_shows_the_failing_disk(monkeypatch, capsys, error, argv):
    # -M and -F drop the whole disk's own row (it is not mounted, or has no type): its SMART comes through its
    # mounted volumes, so a row dropped for their size would hide the failing disk.
    run = _mac(monkeypatch, "/dev/disk3")
    names = {  # disk1's mounted volumes are healthy, but their use was not read: unknown rows beside the problem
        (): ["disk1s1", "disk1s2", "disk1s3"] + DISK3,
        ("-M",): MOUNTED,
        ("-F",): ["disk1s1", "disk1s2", "disk1s3"] + [n for n in DISK3 if n != "disk3"],  # disk3 has no type
    }[tuple(argv)]
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run, usage=error) == (1, names, "T\n", "")


# Linux: sda1 is mounted at /; sdb fails its SMART, and its filesystem sdb1 is not mounted (or, where a case says so,
# mounted at /mnt/b).

LSBLK = [
    'NAME="/dev/sda" SIZE="1073741824" FSTYPE="" UUID="" LABEL="" MODEL="M" SERIAL="S1"',
    'NAME="/dev/sda1" SIZE="1073741824" FSTYPE="ext4" UUID="u1" LABEL="" MODEL="" SERIAL=""',
    'NAME="/dev/sdb" SIZE="1073741824" FSTYPE="" UUID="" LABEL="" MODEL="M" SERIAL="S2"',
    'NAME="/dev/sdb1" SIZE="1073741824" FSTYPE="ext4" UUID="u2" LABEL="" MODEL="" SERIAL=""',
]
LSBLK_STOPPED = {"stopped": ([], CUT), "still running": ([], None, True)}
SDB1_MOUNTED = "101 99 8:17 / /mnt/b rw,relatime - ext4 /dev/sdb1 rw\n"


def _linux(monkeypatch, tmp_path, failing, lsblk=(LSBLK, 0), sdb1_mounted=False):
    mountinfo = tmp_path / "mountinfo"
    mountinfo.write_text("100 99 8:1 / / rw,relatime - ext4 /dev/sda1 rw\n" + (SDB1_MOUNTED if sdb1_mounted else ""))
    monkeypatch.setattr(statblk, "IS_DARWIN", False)
    monkeypatch.setattr(statblk, "MOUNTINFO_PATH", str(mountinfo))
    monkeypatch.setattr(statblk, "get_blocks", lambda: ["/dev/sda", "/dev/sda1", "/dev/sdb", "/dev/sdb1"])
    monkeypatch.setattr(statblk, "is_block_device", lambda p: True)
    monkeypatch.setattr(statblk, "get_partition_parent_name", lambda p: p.rstrip("0123456789") if p else None)
    monkeypatch.setattr(statblk, "has_sysfs_device", lambda disk: True)
    monkeypatch.setattr(statblk, "read_size", lambda p: 1 << 30)  # what sysfs says when lsblk gave no size
    monkeypatch.setattr(statblk, "read_model_and_serial", lambda p: ("", ""))
    monkeypatch.setattr(statblk, "read_discard_support", lambda p: "N/A")
    monkeypatch.setattr(statblk, "build_symlink_dict", lambda d: {})
    monkeypatch.setattr(statblk, "get_read_write_rate_throughput_iter", lambda p: iter(lambda: (0, 0), None))

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
        1, ["sdb", "sdb1"], "T\n", _cut_line("lsblk", 0.5, NOT_FOUND))


def test_linux_formated_only_without_lsblk_says_why_it_filters_nothing(monkeypatch, capsys, tmp_path):
    # -F needs FSTYPE without showing it: 1.63 kept every unmounted device (its type was not read) and said nothing.
    run = _linux(monkeypatch, tmp_path, "/dev/none", lsblk=([], NOT_FOUND))
    assert _run(monkeypatch, capsys, ["-F", "-o", "NAME,SIZE", "-t", "0.5"], run) == (
        0, ["sda", "sda1", "sdb", "sdb1"], "T\n", _cut_line("lsblk", 0.5, NOT_FOUND))


@pytest.mark.parametrize("stop", LSBLK_STOPPED)
def test_linux_formated_only_lsblk_stopped_on_a_healthy_host_is_healthy_and_silent(monkeypatch, capsys, tmp_path, stop):
    run = _linux(monkeypatch, tmp_path, "/dev/none", lsblk=LSBLK_STOPPED[stop])
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "-F"], run) == (0, [], "", "")


@pytest.mark.parametrize("stop", LSBLK_STOPPED)
def test_linux_lsblk_stopped_without_formated_only_is_healthy_and_silent(monkeypatch, capsys, tmp_path, stop):
    # The commonest stop: no -F and no pattern. Sizes come from sysfs, so every row is still there and judged.
    run = _linux(monkeypatch, tmp_path, "/dev/none", lsblk=LSBLK_STOPPED[stop])
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5"], run) == (0, [], "", "")


@pytest.mark.parametrize("stop", LSBLK_STOPPED)
def test_linux_lsblk_stopped_without_formated_only_still_shows_the_failing_disk(monkeypatch, capsys, tmp_path, stop):
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=LSBLK_STOPPED[stop])
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5"], run) == (
        1, ["sdb", "sdb1"], "T\n", _cut_line("lsblk", 0.5))


def test_linux_formated_only_lsblk_answered_drops_the_unformatted_rows(monkeypatch, capsys, tmp_path):
    # The control: lsblk answered, so sda and sdb (no filesystem) go, and sdb1 carries sdb's SMART.
    run = _linux(monkeypatch, tmp_path, "/dev/sdb")
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "-F"], run) == (1, ["sdb1"], "T\n", "")


def test_linux_formated_only_still_shows_the_failing_disk_of_a_partition_lsblk_did_not_list(monkeypatch, capsys,
                                                                                                tmp_path):
    # lsblk exited 0 without sdb1 (it appeared after lsblk ran): sdb is listed with no filesystem and goes, but sdb1's
    # blank type was not read, so it stays and carries sdb's SMART (1.63 dropped both and exited 0).
    lsblk = [line for line in LSBLK if 'NAME="/dev/sdb1"' not in line]
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=(lsblk, 0))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "-F"], run) == (1, ["sdb1"], "T\n", "")


@pytest.mark.parametrize("argv, expected", [
    (["sda"], (3, [], "", _cut_line("lsblk", 0.5))),  # a pattern can match a cell lsblk fills
    (["-D", "sda"], (0, [], "", "")),  # -D matches the device names, which no stopped command can leave out
], ids=["pattern", "-D pattern"])
def test_linux_lsblk_stopped_with_a_pattern(monkeypatch, capsys, tmp_path, argv, expected):
    run = _linux(monkeypatch, tmp_path, "/dev/none", lsblk=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5"] + argv, run) == expected


def test_linux_lsblk_stopped_with_a_pattern_and_a_failing_disk_is_a_problem(monkeypatch, capsys, tmp_path):
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=([], CUT))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "sdb"], run) == (
        1, ["sdb", "sdb1"], "T\n", _cut_line("lsblk", 0.5))


@DID_NOT_ANSWER
def test_linux_lsblk_that_did_not_answer_with_a_pattern_only_it_could_match_is_unknown(monkeypatch, capsys, tmp_path,
                                                                                      returncode):
    # sdb fails, and only lsblk's FSTYPE of the unmounted sdb1 matches "ext4" for it (sda1's matches through the mount
    # table). 1.63 exited 0 here for a missing or failing lsblk, and 3 for a stopped one.
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=([], returncode))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "ext4"], run) == (
        3, [], "", _cut_line("lsblk", 0.5, returncode))
    run = _linux(monkeypatch, tmp_path, "/dev/sdb")  # the control: lsblk answered
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "ext4"], run) == (1, ["sdb1"], "T\n", "")


@pytest.mark.parametrize("argv, expected", [([], (0, [], "", "")), (["--show_zero_size_devices"], (1, ["sdb", "sdb1"], "T\n", ""))],
                         ids=["hidden", "shown"])
def test_linux_disk_whose_size_reads_zero_is_checked_only_when_shown(monkeypatch, capsys, tmp_path, argv, expected):
    # lsblk gave sdb and sdb1 a size of 0: a known limitation (docs/limitations.md).
    lsblk = [line.replace('SIZE="1073741824"', 'SIZE="0"') if "sdb" in line else line for line in LSBLK]
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=(lsblk, 0))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5"] + argv, run) == expected


def test_linux_zero_size_whole_disk_is_judged_through_its_partition(monkeypatch, capsys, tmp_path):
    # Only sdb reads 0: sdb1's row is shown and carries sdb's SMART (the known limitation needs no partition row).
    lsblk = [line.replace('SIZE="1073741824"', 'SIZE="0"') if 'NAME="/dev/sdb"' in line else line for line in LSBLK]
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=(lsblk, 0))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5"], run) == (1, ["sdb1"], "T\n", "")


@pytest.mark.parametrize("lsblk", [([], NOT_FOUND), ([], CUT)], ids=["no lsblk", "lsblk stopped"])
def test_linux_failing_disk_whose_sysfs_size_cannot_be_read_is_judged(monkeypatch, capsys, tmp_path, lsblk):
    # With no size from lsblk, sdb's and sdb1's come from sysfs, which no longer answers (the disk is going away): not
    # read is not a size of 0, so the rows stay, SIZE blank, and sdb's SMART is judged (1.63 dropped them, exit 0).
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", lsblk=lsblk)
    monkeypatch.setattr(statblk, "read_size", lambda p: None if "sdb" in p else 1 << 30)
    code, tables, out, err = _run_tables(monkeypatch, capsys, ["--check", "-t", "0.5", "-o", "NAME,SIZE"], run)
    assert (code, out) == (1, "T\n")
    size = tables[0][0].index("SIZE")
    assert [(row[0], row[size]) for row in tables[0][1:]] == [("sdb", ""), ("sdb1", "")]


def test_linux_active_only_judges_a_failing_disk_whose_stat_cannot_be_read(monkeypatch, capsys, tmp_path):
    # -A drops a device read as idle; sdb's stat no longer answers, which is not idle (1.63 read it as 0 B/s, exit 0).
    run = _linux(monkeypatch, tmp_path, "/dev/sdb")
    monkeypatch.setattr(statblk, "get_read_write_rate_throughput_iter",
                        lambda p: iter(lambda: (None, None) if "sdb" in p else (0, 0), None))
    assert _run(monkeypatch, capsys, ["--check", "-t", "0.5", "-A"], run) == (1, ["sdb", "sdb1"], "T\n", "")


@STATVFS_ERRORS
@pytest.mark.parametrize("timeout", ["0", "2"], ids=["no limit", "in a thread"])
def test_linux_statvfs_error_is_unknown_not_healthy(monkeypatch, capsys, tmp_path, error, timeout):
    run = _linux(monkeypatch, tmp_path, "/dev/none")
    code, tables, out, err = _run_tables(monkeypatch, capsys, ["--check", "-t", timeout], run, usage=error)
    assert (code, out, err) == (3, "T\n", "")
    use = tables[0][0].index("FSUSE%")
    assert [(row[0], row[use]) for row in tables[0][1:]] == [("sda1", "ERROR")]


@STATVFS_ERRORS
@pytest.mark.parametrize("argv", [[], ["-M"], ["-F"]], ids=["plain", "-M", "-F"])
def test_linux_statvfs_error_still_shows_the_failing_disk(monkeypatch, capsys, tmp_path, error, argv):
    # sdb1 is mounted and its statvfs fails. -M and -F drop sdb itself (not mounted, no filesystem type): its SMART
    # comes through sdb1, and a row dropped for its size would hide the failing disk.
    run = _linux(monkeypatch, tmp_path, "/dev/sdb", sdb1_mounted=True)
    names = ["sda1", "sdb", "sdb1"] if not argv else ["sda1", "sdb1"]
    assert _run(monkeypatch, capsys, ["--check", "-t", "2"] + argv, run, usage=error) == (1, names, "T\n", "")


@pytest.mark.parametrize("usage, cell", [(DENIED, "ERROR"), (None, "TIMEOUT")], ids=["error", "hang"])
def test_linux_watch_keeps_an_idle_devices_failed_mount_after_the_first_refresh(monkeypatch, capsys, tmp_path, usage,
                                                                                 cell):
    # Watch mode turns -A on after its first refresh, and every device here reads as idle: sda1's mount row, whose
    # statvfs fails or hangs, stays in the second table (1.63 showed it once).
    run = _linux(monkeypatch, tmp_path, "/dev/none")
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        if len(sleeps) == 2:
            raise KeyboardInterrupt()

    monkeypatch.setattr(statblk.time, "sleep", sleep)
    code, tables, out, err = _run_tables(monkeypatch, capsys, ["-w", "1", "-t", "2", "-o", "NAME,FSUSE%"], run, usage)
    assert code == 130 and len(tables) == 2
    assert ["sda1", cell] in tables[0] and tables[1][1:] == [["sda1", cell]]


# The cut rule, one case per cell, through the real get_drives_info: a healthy host whose command --timeout stopped
# before it printed anything. A stopped command hides a checked column from the check only where its answer is that
# column's input: macOS's mount lists the mounted filesystems (their FSUSE%, and with -M the rows that carry the SMART),
# and a pattern that is not -D matches any cell a command fills. Everything else is shown blank and judged as before.

CUT_FLAGS = {
    "plain": [], "-M": ["-M"], "-F": ["-F"], "-F -M": ["-F", "-M"],
    "pattern": ["sda"], "-D pattern": ["-D", "sda"], "-M pattern": ["-M", "sda"],
}
CUT_COLUMNS = {  # the checked columns shown, and the -x that leaves them
    "FSUSE%": ["-x", "SMART"], "SMART": ["-x", "FSUSE%"], "both": [],
}
_PATTERNS = {"pattern", "-M pattern"}
_CUT_COUNTS = {  # command, checked columns shown: the flag sets under which the cut makes a healthy run exit 3
    ("mount", "FSUSE%"): set(CUT_FLAGS),
    ("mount", "SMART"): {"-M", "-F -M"} | _PATTERNS,
    ("diskutil", "FSUSE%"): _PATTERNS,
    ("diskutil", "SMART"): _PATTERNS,
    ("lsblk", "FSUSE%"): _PATTERNS,
    ("lsblk", "SMART"): _PATTERNS,
}
for _command in ("mount", "diskutil", "lsblk"):
    _CUT_COUNTS[(_command, "both")] = _CUT_COUNTS[(_command, "FSUSE%")] | _CUT_COUNTS[(_command, "SMART")]


@DID_NOT_ANSWER
@pytest.mark.parametrize("flags", CUT_FLAGS)
@pytest.mark.parametrize("columns", CUT_COLUMNS)
@pytest.mark.parametrize("command", ["mount", "diskutil", "lsblk"])
def test_check_cut_rule_cell(monkeypatch, capsys, tmp_path, command, columns, flags, returncode):
    # One rule however the command did not answer: stopped by --timeout, not found or failed (1.63 counted only a stop).
    if command == "lsblk":
        run = _linux(monkeypatch, tmp_path, "/dev/none", lsblk=([], returncode))
    elif command == "mount":
        run = _mac(monkeypatch, "/dev/none", mount=([], returncode))
    else:
        run = _mac(monkeypatch, "/dev/none", diskutil=([], returncode))
    argv = ["--check", "-t", "0.5"] + CUT_COLUMNS[columns] + CUT_FLAGS[flags]
    expected = ((3, [], "", _cut_line(command, 0.5, returncode)) if flags in _CUT_COUNTS[(command, columns)]
                else (0, [], "", ""))
    assert _run(monkeypatch, capsys, argv, run) == expected
